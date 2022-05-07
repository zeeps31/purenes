from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture

from purenes.ppu import PPU


class TestPPU(object):

    TOTAL_SCANLINES: int = 262

    TOTAL_VISIBLE_SCANLINES: int = 240

    TOTAL_SCANLINE_CYCLES: int = 341

    TOTAL_VISIBLE_SCANLINE_CYCLES: int = 257

    def test_ppu_reset(self, ppu: PPU):
        ppu.reset()

        assert ppu.control.reg == 0
        assert ppu.status.reg == 0
        assert ppu.vram.reg == 0
        assert ppu.vram_temp.reg == 0
        assert ppu.write_latch == 0

    def test_nametable_reads_during_a_scanline_cycle(
            self,
            ppu: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Tests reads to retrieve nametable data during scanline cycles.

        Note:
            This test uses the pre-render scanline to perform tests. Memory
            access during this scanline is the same as a normal scanline.

        Verifies that reads to retrieve nametable data for the current scanline
        (cycles 0-256) and the next scanline (cycles 321-340) are correct.
        """
        ppu.write(0x2006, 0x20)
        ppu.write(0x2006, 0x00)

        for _ in range(0, self.TOTAL_SCANLINE_CYCLES):
            ppu.clock()

        current_scanline_reads = [
            mocker.call.read(0x2000 + coarse_x) for coarse_x in range(0, 32)
        ]
        # Unused fetches at the end of the scanline are not included in testing
        next_scanline_reads = [
            mocker.call.read(0x2000 + coarse_x) for coarse_x in range(0, 2)
        ]

        mock_ppu_bus.read.assert_has_calls(
            current_scanline_reads + next_scanline_reads,
            any_order=True
        )

    def test_attribute_table_reads_during_a_scanline_cycle(
            self,
            ppu: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Tests reads to retrieve attribute table data during scanline cycles.

        Note:
            This test uses the pre-render scanline to perform tests. Memory
            access during this scanline is the same as a normal scanline.

        Verifies that reads to retrieve attribute table bytes for the current
        scanline (cycles 0-256) and the next scanline (cycles 321-340) are
        correct.
        """
        ppu.write(0x2006, 0x20)
        ppu.write(0x2006, 0x00)

        for _ in range(0, self.TOTAL_SCANLINE_CYCLES):
            ppu.clock()

        # Each attribute table byte "controls" one 4x4 section of tiles. There
        # are 8 sections of 4 tiles across the horizontal axis for the visible
        # part of the scanline and 4 calls should be made to the same address
        # for one section.
        current_scanline_reads = [
            mocker.call.read(0x23C0 + coarse_x) for _ in range(0, 4)
            for coarse_x in range(0, 8)
        ]
        # Unused fetches at the end of the scanline are not included in testing
        next_scanline_reads = [mocker.call.read(0x23C0) for _ in range(0, 2)]

        mock_ppu_bus.read.assert_has_calls(
            current_scanline_reads + next_scanline_reads,
            any_order=True
        )

    def test_pattern_table_reads_during_a_scanline_cycle(
            self,
            ppu: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Tests reads to retrieve low and high pattern table tiles during a
        scanline cycle.

        Note:
            This test uses the pre-render scanline to perform tests. Memory
            access during this scanline is the same as a normal scanline.

        Verifies that each rendering cycle makes two calls to retrieve the low
        and high bytes of a pattern table tile correctly.

        In this test the the background_pt_address in the _Control register is
        set to 0 (by default) and fine_y is explicitly set to 0.
        """
        ppu.write(0x2005, 0x00)
        ppu.write(0x2000, 0x00)  # Set fine_y to 0

        ppu.write(0x2006, 0x20)
        ppu.write(0x2006, 0x00)

        mock_ppu_bus.read.return_value = 0x01  # Pattern tile ID

        for _ in range(0, self.TOTAL_SCANLINE_CYCLES):
            ppu.clock()

        # background_pt_address and fine_y are set to 0 and the pattern tile
        # returned from the mocked PPUBus is 0x01
        expected_pt_address: int = 0x10
        current_scanline_reads = []
        next_scanline_reads = []

        for _ in range(0, 32):
            current_scanline_reads.append(
                mocker.call.read(expected_pt_address))
            current_scanline_reads.append(
                mocker.call.read(expected_pt_address + 8))

        # fine_y is incremented by 1 at the end of the visible scanline cycles
        # for the prefetches at the end of the scanline.
        for _ in range(0, 2):
            next_scanline_reads.append(
                mocker.call.read(expected_pt_address + 1))
            next_scanline_reads.append(
                mocker.call.read(expected_pt_address + 1 + 8))

        mock_ppu_bus.read.assert_has_calls(
            current_scanline_reads + next_scanline_reads,
            any_order=True
        )

    def test_coarse_scroll_horizontal_increment(self, ppu: PPU):
        """Tests coarse_x increment without scrolling offsets

        Verifies that coarse_x is 31 (the last tile of the nametable) and that
        the nametable address was not wrapped around.
        """
        ppu.write(0x2006, 0x20)
        ppu.write(0x2006, 0x00)

        for _ in range(0, self.TOTAL_VISIBLE_SCANLINE_CYCLES):
            ppu.clock()

        assert ppu.vram.flags.coarse_x == 0x1F
        assert ppu.vram.flags.nt_select_x == 0

    def test_coarse_scroll_horizontal_increment_wraps_around_at_maximum(
            self,
            ppu: PPU
    ):
        """Tests coarse_x increment with scrolling offsets

        Verifies that coarse_x is 0 (the first tile of the next nametable) and
        that the nametable address was wrapped around after offsetting coarse_x
        by 1.
        """
        ppu.write(0x2006, 0x20)
        ppu.write(0x2006, 0x01)

        for _ in range(0, self.TOTAL_VISIBLE_SCANLINE_CYCLES):
            ppu.clock()

        assert ppu.vram.flags.coarse_x == 0x00
        assert ppu.vram.flags.nt_select_x == 1

    def test_horizontal_coarse_scroll_resets_after_rendering_a_scanline(
            self,
            ppu: PPU
    ):
        """Tests coarse_x resets at cycle 257 in a scanline during rendering.
        """
        for _ in range(0, self.TOTAL_VISIBLE_SCANLINE_CYCLES + 1):
            ppu.clock()

        assert ppu.vram.flags.coarse_x == 0

    def test_vertical_scrolling(self, ppu: PPU):
        """Tests vertical scrolling without any vertical scrolling offsets.

        Verifies that fine_y is incremented by 1 without overflowing into
        coarse_y
        """
        ppu.write(0x2005, 0x00)
        ppu.write(0x2000, 0x00)

        for _ in range(0, self.TOTAL_VISIBLE_SCANLINE_CYCLES):
            ppu.clock()

        assert ppu.vram.flags.fine_y == 1
        assert ppu.vram.flags.coarse_y == 0
        assert ppu.vram.flags.nt_select_y == 0

    def test_vertical_scrolling_overflows_at_maximum(
            self,
            ppu: PPU
    ):
        """Tests vertical scrolling with a fine_y offset of 1 overflows into
        coarse_y after one row of tiles is rendered.

        Sets fine_y = 1 and clocks the PPU for the total number of cycles
        required to render a full row of 8x8 tiles. Verifies that fine_y is
        reset and coarse_y is incremented once the maximum is reached.
        """
        ppu.write(0x2005, 0x00)
        ppu.write(0x2000, 0x01)

        for _ in range(0, self.TOTAL_SCANLINE_CYCLES * 8):
            ppu.clock()

        assert ppu.vram.flags.fine_y == 0
        assert ppu.vram.flags.coarse_y == 1
        assert ppu.vram.flags.nt_select_y == 0

    def test_vertical_scrolling_wraps_around_nametable_at_maximum(
            self,
            ppu: PPU
    ):
        """Tests vertical scrolling with a fine_y offset of 1 wraps around the
        nametable after one frame is rendered.

        Verifies that the vertical nametable is wrapped around once the
        maximum is reached.
        """
        ppu.write(0x2005, 0x00)
        ppu.write(0x2000, 0x01)  # Set fine_y

        range_max: int = (self.TOTAL_SCANLINE_CYCLES *
                          self.TOTAL_VISIBLE_SCANLINES)
        for _ in range(0, range_max):
            ppu.clock()

        assert ppu.vram.flags.fine_y == 0
        assert ppu.vram.flags.coarse_y == 0
        assert ppu.vram.flags.nt_select_y == 1

    def test_cycle_resets_at_maximum(self, ppu: PPU):
        """Tests incrementing of cycles within a scanline resets at the maximum
        and that the scanline is incremented by 1.

        The PPU is clocked for one full scanline to verify the cycle counter
        is reset when the maximum is reached and the scanline is incremented.
        """
        for _ in range(0, self.TOTAL_SCANLINE_CYCLES):
            ppu.clock()

        assert ppu.cycle == 0
        assert ppu.scanline == 0

    def test_scanline_resets_at_maximum(self, ppu: PPU):
        """Tests scanline is reset to the pre-render scanline when the maximum
        scanline and scanline cycles have been reached.
        """
        for _ in range(0, self.TOTAL_SCANLINE_CYCLES * self.TOTAL_SCANLINES):
            ppu.clock()

        assert ppu.scanline == -1

    @pytest.mark.parametrize(
        "cycle_count, at_shift_hi, at_shift_lo", [
            (10, 255, 255),
            (18, 65535, 65535),
            (258, 65535, 65535),
            (322, 65535, 65535),
            (330, 65535, 65535)
        ]
    )
    def test_palette_selection_while_rendering(
            self,
            ppu: PPU,
            mock_ppu_bus: Mock,
            cycle_count,
            at_shift_hi,
            at_shift_lo
    ):
        """Tests attribute table shift registers are loaded and shifted
        correctly during rendering cycles.

        The shift registers are reloaded during cycles 9, 17, 25, ..., 257
        and cycles 329 and 327.
        """
        # Return value for attribute table reads
        mock_ppu_bus.read.return_value = 0xFF

        for _ in range(0, cycle_count):
            ppu.clock()

        assert ppu.at_shift_hi == at_shift_hi
        assert ppu.at_shift_lo == at_shift_lo

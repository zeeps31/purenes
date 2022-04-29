from unittest.mock import Mock

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
        """Test reads to retrieve nametable data during scanline cycles.

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
            current_scanline_reads + next_scanline_reads
        )

    def test_coarse_scroll_horizontal_increment(self, ppu: PPU):
        """Test coarse_x increment without scrolling offsets

        Sets coarse_x = 0 and clocks the PPU 256 times. Verifies that
        coarse_x is 31 (the last tile of the nametable) and that the
        nametable address was not wrapped around.
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
        """Test coarse_x increment with scrolling offsets

        Sets coarse_x = 1 and clocks the PPU 256 times. Verifies that
        coarse_x is 0 (the first tile of the next nametable) and that the
        nametable address is wrapped around.
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
        """Tests coarse_x reset at cycle 257 in a scanline during rendering.

        Clocks the PPU 258 times (cycles 0 - 257) and verifies that coarse_x is
        reset at cycle 257.
        """
        for _ in range(0, self.TOTAL_VISIBLE_SCANLINE_CYCLES + 1):
            ppu.clock()

        assert ppu.vram.flags.coarse_x == 0

    def test_vertical_scrolling(self, ppu: PPU):
        """Test vertical scrolling without any vertical scrolling offsets.

        Sets fine_y = 0 and clocks the PPU 257 (include cycle 256) times.
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
        """Test vertical scrolling with a fine_y offset of 1 overflows into
        coarse_y after one tile is rendered.

        Sets fine_y = 1 and clocks the PPU 2,720 times (total cycles to render
        a full row of 8x8 tiles). Verifies that fine_y is reset and coarse_y is
        incremented once the maximum is reached.
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
        """Test vertical scrolling with a fine_y offset of 1 wraps around the
        nametable after one frame is rendered.

        Sets fine_y = 1 and clocks the PPU . Verifies that the
        vertical nametable is wrapped around once the maximum is reached.
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
        """Test incrementing of cycles within a scanline resets at the maximum
        and that the scanline is incremented by 1.

        There are 341 cycles per scanline. The PPU is clocked 341 times to
        verify the cycle counter is reset when the maximum is reached and the
        scanline is incremented.
        """
        for _ in range(0, 341):
            ppu.clock()

        assert ppu.cycle == 0
        assert ppu.scanline == 0

    def test_scanline_resets_at_maximum(self, ppu: PPU):
        """Test scanline is reset to the pre-render scanline when the maximum
        scanline and scanline cycles have been reached.
        """
        for _ in range(0, self.TOTAL_SCANLINE_CYCLES * self.TOTAL_SCANLINES):
            ppu.clock()

        assert ppu.scanline == -1

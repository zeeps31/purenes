from unittest import mock

import pytest
import pytest_mock

import purenes.ppu


class TestPPURegisters(object):
    """Suite of tests to test reads and writes to the internal PPU registers.

    There are quite a few nuances associated with reading and writing to these
    registers that warrant a dedicated suite of tests.
    """

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_write_to_control_register(self, ppu: purenes.ppu.PPU, data: int):
        """Test write to $2000. Verifies the flags of the control register are
        updated and that the vram_temp.nt_select_x and vram_temp.nt_select_y
        attributes are updated when a write to $2000 occurs.
        """
        address = 0x2000

        ppu.write(address, data)

        control = ppu.read_only_values["control"]
        vram = ppu.read_only_values["vram"]
        vram_temp = ppu.read_only_values["vram_temp"]
        assert control.reg == data
        assert vram.reg == 0  # Assert not updated
        assert control.flags.base_nt_address == (data >> 0) & 3
        assert control.flags.vram_address_increment == (data >> 2) & 1
        assert control.flags.sprite_pt_address == (data >> 3) & 1
        assert control.flags.background_pt_address == (data >> 4) & 1
        assert control.flags.sprite_size == (data >> 5) & 1
        assert control.flags.ppu_leader_follower == (data >> 6) & 1
        assert control.flags.generate_nmi == (data >> 7) & 1
        assert vram_temp.flags.nt_select_x == (data >> 0) & 0x01
        assert vram_temp.flags.nt_select_y == (data >> 1) & 0x01

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_write_to_mask_register(self, ppu: purenes.ppu.PPU, data: int):
        """Test PPUMASK $2001 write.

        Verifies that all flags are set appropriately for a given input.
        """
        address = 0x2001

        ppu.write(address, data)

        mask = ppu.read_only_values["mask"]
        assert mask.flags.greyscale == (data >> 0) & 1
        assert mask.flags.show_background_leftmost == (data >> 1) & 1
        assert mask.flags.show_sprites_leftmost == (data >> 2) & 1
        assert mask.flags.show_background == (data >> 3) & 1
        assert mask.flags.show_sprites == (data >> 4) & 1
        assert mask.flags.emphasize_red == (data >> 5) & 1
        assert mask.flags.emphasize_green == (data >> 6) & 1
        assert mask.flags.emphasize_blue == (data >> 7) & 1

    def test_read_from_status_register_resets_write_latch(
            self,
            ppu: purenes.ppu.PPU
    ):
        """Test PPUSTATUS $2002

        Verifies the internal write latch is reset for each read from this
        address location.
        """
        address = 0x2002

        ppu.read(address)

        assert ppu.read_only_values["write_latch"] == 0

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_write_to_scroll_register(self, ppu: purenes.ppu.PPU, data: int):
        """Test PPUSCROLL $2005 write.

        Verifies that on the first write to $2005 bits 3-7 of the input data
        are used to set coarse_x in t, bits 0-2 are used to set fine_x and
        the write_latch is updated to 1. On the second write bits 3-7 of the
        input data are used to set coarse_y in t, bits 0-2 are used to set
        fine_y and the write_latch is set to 0.
        """
        address = 0x2005

        # First write
        ppu.write(address, data)

        vram_temp = ppu.read_only_values["vram_temp"]
        assert vram_temp.flags.coarse_x == data >> 3
        assert ppu.read_only_values["fine_x"] == data & 0x07
        assert ppu.read_only_values["write_latch"] == 1

        # Second write
        ppu.write(address, data)

        assert vram_temp.flags.coarse_y == data >> 3
        assert vram_temp.flags.fine_y == data & 0x07
        assert ppu.read_only_values["write_latch"] == 0

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_write_to_vram_address_register(
            self,
            ppu: purenes.ppu.PPU,
            data: int
    ):
        """Test writes to $2006. Writing to $2006 requires two writes to set
        the VRAM address.

        Verifies on the first write vram_temp is updated correctly and the
        write_latch is set to 1. On the second write verifies the internal
        write_latch is set to 0, the full address is transferred from
        t -> v and all of the flags are set correctly.
        """
        address = 0x2006
        vram_address = (data << 8) | data  # Full 16-bit address

        vram = ppu.read_only_values["vram"]
        vram_temp = ppu.read_only_values["vram_temp"]

        ppu.write(address, data)

        # Verify t: .CDEFGH ........ <- d: ..CDEFGH
        assert ((vram_temp.reg >> 8) & 0x3F) == (data & 0x3F)
        assert ppu.read_only_values["write_latch"] == 1

        ppu.write(address, data)

        # Verify t: ....... ABCDEFGH <- d: ABCDEFGH
        assert vram.reg == ((data & 0x3F) << 8) | data
        # Verify v: <...all bits...> <- t: <...all bits...>
        assert vram.reg == vram_temp.reg
        assert ppu.read_only_values["write_latch"] == 0
        # Assert flags set correctly
        assert vram.flags.coarse_x == vram_address & 0x1F
        assert vram.flags.coarse_y == (vram_address >> 5) & 0x1F
        assert vram.flags.nt_select_x == (vram_address >> 10) & 0x01
        assert vram.flags.nt_select_y == (vram_address >> 11) & 0x01

    def test_write_to_data_register_with_horizontal_increment_mode(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock,
            mocker: pytest_mock.MockFixture
    ):
        """Test PPUDATA $2007 write x increment.

        Test that successive writes to the data register with increment_mode
        0 increments the vram address by one byte.
        """
        address = 0x2007
        data = 0x01

        ppu.write(address, data)
        ppu.write(address, data)

        mock_ppu_bus.write.assert_has_calls([
            mocker.call.write(0x0000, 0x01),
            mocker.call.write(0x0001, 0x01)
        ])

    def test_write_to_data_register_with_vertical_increment_mode(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock,
            mocker: pytest_mock.MockFixture
    ):
        """Test PPUDATA $2007 write y increment.

        Test that successive writes to the data register with increment_mode
        1 increment the vram address by 32 bytes.
        """
        address = 0x2007
        data = 0x01

        ppu.write(0x2000, 0x4)  # Set the increment mode

        ppu.write(address, data)
        ppu.write(address, data)

        mock_ppu_bus.write.assert_has_calls([
            mocker.call.write(0x0000, 0x01),
            mocker.call.write(0x0020, 0x01)
        ])

    def test_read_from_data_register_with_horizontal_increment_mode(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock,
            mocker: pytest_mock.MockFixture
    ):
        """Test PPUDATA $2007 x increment.

        Test that successive reads from the data register with increment_mode
        0 increment the vram address by one byte.
        """
        address = 0x2007

        ppu.read(address)
        ppu.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0001)
        ])

    def test_read_from_data_register_with_vertical_increment_mode(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock,
            mocker: pytest_mock.MockFixture
    ):
        """Test PPUDATA $2007 y increment.

        Test that successive reads from the data register with increment_mode
        1 increments the vram address by 32 bytes.
        """
        address = 0x2007

        ppu.write(0x2000, 0x4)

        ppu.read(address)
        ppu.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0020)
        ])

    def test_read_from_data_register_non_palette_address_buffers_value(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock
    ):
        """Test PPUDATA $2007 read for non-palette address 0-$3EFF.

        Test that successive reads from $2007 for VVRAM addresses <= $3EFF
        are buffered and delayed by one frame
        """
        address = 0x2007
        expected_values = [0x00, 0x00, 0x01]
        actual_values = []

        mock_ppu_bus.read.side_effect = [
            0x00,
            0x01,
            0x02
        ]

        actual_values.append(ppu.read(address))
        actual_values.append(ppu.read(address))
        actual_values.append(ppu.read(address))

        assert actual_values == expected_values

    def test_read_from_data_register_palette_address_does_not_buffer_value(
            self,
            ppu: purenes.ppu.PPU,
            mock_ppu_bus: mock.Mock
    ):
        """Tests PPUDATA $2007 read for addresses >= $3F00.

        Test that successive reads to $2007 for VVRAM addresses >= $3F00
        are not buffered and returned immediately.
        """
        address = 0x2007
        expected_values = [0x00, 0x01, 0x02]
        actual_values = []

        ppu.write(0x2006, 0x3F)  # VRAM address high-byte
        ppu.write(0x2006, 0x00)  # VRAM address low-byte
        mock_ppu_bus.read.side_effect = [
            0x00,
            0x01,
            0x02
        ]

        actual_values.append(ppu.read(address))
        actual_values.append(ppu.read(address))
        actual_values.append(ppu.read(address))

        assert actual_values == expected_values

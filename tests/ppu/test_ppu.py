import pytest

from unittest.mock import Mock
from pytest_mock import MockFixture

from purenes.ppu import PPU


class TestPPU(object):

    @pytest.fixture()
    def mock_ppu_bus(self, mocker: MockFixture):
        yield mocker.Mock()

    @pytest.fixture()
    def test_object(self, mock_ppu_bus: Mock):
        yield PPU(mock_ppu_bus)

    @pytest.fixture(autouse=True)
    def before_each(self, test_object: PPU):
        test_object.reset()

    def test_ppu_reset(self, test_object: PPU):
        test_object.reset()

        assert test_object.control.reg == 0
        assert test_object.status.reg == 0
        assert test_object.vram.reg == 0
        assert test_object.vram_temp.reg == 0
        assert test_object.write_latch == 0

    def test_coarse_x_increment(self, test_object: PPU):
        """Test coarse_x increment without scrolling offsets

        Sets coarse_x = 0 and clocks the PPU 256 times. Verifies that
        coarse_x is 31 (the last tile of the nametable) and that the
        nametable address was not wrapped around.
        """
        test_object.write(0x2006, 0x20)
        test_object.write(0x2006, 0x00)

        for i in range(0, 257):
            test_object.clock()

        assert test_object.vram.flags.coarse_x == 0x1F
        assert test_object.vram.flags.nt_select == 0

    def test_coarse_x_increment_wrap(self, test_object: PPU):
        """Test coarse_x increment with scrolling offsets

        Sets coarse_x = 1 and clocks the PPU 256 times. Verifies that
        coarse_x is 0 (the first tile of the next nametable) and that the
        nametable address is wrapped around.
        """
        test_object.write(0x2006, 0x20)
        test_object.write(0x2006, 0x01)

        for i in range(0, 257):
            test_object.clock()

        assert test_object.vram.flags.coarse_x == 0x00
        assert test_object.vram.flags.nt_select == 1

    def test_cycle_incremented_at_maximum(self, test_object: PPU):
        """Test incrementing of cycles within a scanline resets at the maximum
        and that the scanline is incremented by 1.

        There are 341 cycles per scanline. The PPU is clocked 341 times to
        verify the cycle counter is reset when the maximum is reached and the
        scanline is incremented.
        """
        for _ in range(0, 341):
            test_object.clock()

        assert test_object.cycle == 0
        assert test_object.scanline == 0

    def test_scanline_resets_at_maximum(self, test_object: PPU):
        """Test scanline is reset to the pre-render scanline when the maximum
        scanline and scanline cycles have been reached.
        """
        for _ in range(0, 341 * 262):  # 341 cycles and 261 scanlines
            test_object.clock()

        assert test_object.scanline == -1

    # Test internal registers
    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_control_write(self, test_object: PPU, data: int):
        """Test write to $2000. Verifies the flags of the control register are
        updated and that the vram_temp.nt_select attribute is updated when a
        write to $2000 occurs.
        """
        address = 0x2000

        test_object.write(address, data)

        control = test_object.control
        vram = test_object.vram
        vram_temp = test_object.vram_temp
        assert control.reg == data
        assert vram.reg == 0  # Assert not updated
        assert control.flags.base_nt_address == (data >> 0) & 3
        assert control.flags.vram_address_increment == (data >> 2) & 1
        assert control.flags.sprite_pt_address == (data >> 3) & 1
        assert control.flags.background_pt_address == (data >> 4) & 1
        assert control.flags.sprite_size == (data >> 5) & 1
        assert control.flags.ppu_leader_follower == (data >> 6) & 1
        assert control.flags.generate_nmi == (data >> 7) & 1
        assert vram_temp.flags.nt_select == (data >> 0) & 3

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_mask_write(self, test_object: PPU, data: int):
        """Test PPUMASK $2001 write.

        Verifies that all flags are set appropriately for a given input.
        """
        address = 0x2001

        test_object.write(address, data)

        mask = test_object.mask
        assert mask.flags.greyscale == (data >> 0) & 1
        assert mask.flags.show_background_leftmost == (data >> 1) & 1
        assert mask.flags.show_sprites_leftmost == (data >> 2) & 1
        assert mask.flags.show_background == (data >> 3) & 1
        assert mask.flags.show_sprites == (data >> 4) & 1
        assert mask.flags.emphasize_red == (data >> 5) & 1
        assert mask.flags.emphasize_green == (data >> 6) & 1
        assert mask.flags.emphasize_blue == (data >> 7) & 1

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_scroll_write(self, test_object: PPU, data: int):
        """Test PPUSCROLL $2005 write.

        Verifies that on the first write to $2005 bits 3-7 of the input data
        are used to set coarse_x in t, bits 0-2 are used to set fine_x and
        the write_latch is updated to 1. On the second write bits 3-7 of the
        input data are used to set coarse_y in t, bits 0-2 are used to set
        fine_y and the write_latch is set to 0.
        """
        address = 0x2005

        # First write
        test_object.write(address, data)

        vram_temp = test_object.vram_temp
        assert vram_temp.flags.coarse_x == data >> 3
        assert test_object.fine_x == data & 0x07
        assert test_object.write_latch == 1

        # Second write
        test_object.write(address, data)

        assert vram_temp.flags.coarse_y == data >> 3
        assert vram_temp.flags.fine_y == data & 0x07
        assert test_object.write_latch == 0

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_vram_address_write(self, test_object: PPU, data: int):
        # TODO: https://github.com/zeeps31/purenes/issues/28
        """Test writes to $2006. Writing to $2006 requires two writes to set
        the VRAM address.

        Verifies on the first write vram_temp is updated correctly and the
        write_latch is set to 1 and on the second write verifies the internal
        write_latch is set to 0 and the full address is transferred from
        t -> v and all of the flags are set correctly.
        """
        address = 0x2006
        vram_address = (data << 8) | data  # Full 16-bit address

        vram = test_object.vram
        vram_temp = test_object.vram_temp

        test_object.write(address, data)

        # Verify t: .CDEFGH ........ <- d: ..CDEFGH
        assert ((vram_temp.reg >> 8) & 0x3F) == (data & 0x3F)
        assert test_object.write_latch == 1

        test_object.write(address, data)

        # Verify t: ....... ABCDEFGH <- d: ABCDEFGH
        assert vram.reg == ((data & 0x3F) << 8) | data
        # Verify v: <...all bits...> <- t: <...all bits...>
        assert vram.reg == vram_temp.reg
        assert test_object.write_latch == 0
        # Assert flags set correctly
        assert vram.flags.coarse_x == vram_address & 0x1F
        assert vram.flags.coarse_y == (vram_address >> 5) & 0x1F
        assert vram.flags.nt_select == (vram_address >> 10) & 0x03

    def test_data_write_x_increment(
            self,
            test_object: PPU,
            mock_ppu_bus,
            mocker
    ):
        """Test PPUDATA $2007 write x increment.

        Test that successive writes to the data register with increment_mode
        0 increments the vram address by one byte.
        """
        address = 0x2007
        data = 0x01

        test_object.write(address, data)
        test_object.write(address, data)

        mock_ppu_bus.write.assert_has_calls([
            mocker.call.write(0x0000, 0x01),
            mocker.call.write(0x0001, 0x01)
        ])

    def test_data_write_y_increment(
            self,
            test_object: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Test PPUDATA $2007 write y increment.

        Test that successive writes to the data register with increment_mode
        1 increments the vram address by 32 bytes.
        """
        address = 0x2007
        data = 0x01

        test_object.write(0x2000, 0x4)  # Set the increment mode

        test_object.write(address, data)
        test_object.write(address, data)

        mock_ppu_bus.write.assert_has_calls([
            mocker.call.write(0x0000, 0x01),
            mocker.call.write(0x0020, 0x01)
        ])

    def test_status_read(self, test_object: PPU):
        address = 0x2002

        test_object.read(address)

        assert test_object.write_latch == 0

    def test_data_read_x_increment(
            self,
            test_object: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Test PPUDATA $2007 x increment.

        Test that successive writes to the data register with increment_mode
        0 increments the vram address by one byte.
        """
        address = 0x2007

        test_object.read(address)
        test_object.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0001)
        ])

    def test_data_read_y_increment(
            self,
            test_object: PPU,
            mock_ppu_bus: Mock,
            mocker: MockFixture
    ):
        """Test PPUDATA $2007 y increment.

        Test that successive writes to the data register with increment_mode
        1 increments the vram address by 32 bytes.
        """
        address = 0x2007

        test_object.write(0x2000, 0x4)

        test_object.read(address)
        test_object.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0020)
        ])

    def test_data_read_buffer(self, test_object: PPU, mock_ppu_bus: Mock):
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

        actual_values.append(test_object.read(address))
        actual_values.append(test_object.read(address))
        actual_values.append(test_object.read(address))

        assert actual_values == expected_values

    def test_data_read_buffer_palette_address(
            self,
            test_object: PPU,
            mock_ppu_bus: Mock
    ):
        """Tests PPUDATA $2007 read for addresses >= $3F00.

        Test that successive reads to $2007 for VVRAM addresses >= $3F00
        are not buffered and returned immediately.
        """
        address = 0x2007
        expected_values = [0x00, 0x01, 0x02]
        actual_values = []

        test_object.write(0x2006, 0x3F)  # VRAM address high-byte
        test_object.write(0x2006, 0x00)  # VRAM address low-byte
        mock_ppu_bus.read.side_effect = [
            0x00,
            0x01,
            0x02
        ]

        actual_values.append(test_object.read(address))
        actual_values.append(test_object.read(address))
        actual_values.append(test_object.read(address))

        assert actual_values == expected_values

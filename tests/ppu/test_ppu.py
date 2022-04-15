import pytest
from purenes.ppu import PPU


class TestPPU(object):

    @pytest.fixture()
    def mock_ppu_bus(self, mocker):
        yield mocker.Mock()

    @pytest.fixture()
    def test_object(self, mock_ppu_bus):
        yield PPU(mock_ppu_bus)

    @pytest.fixture(autouse=True)
    def before_each(self, test_object):
        test_object.reset()

    def test_ppu_reset(self, test_object):
        test_object.reset()

        assert(test_object.control.reg == 0)
        assert(test_object.status.reg == 0)
        assert(test_object.vram.reg == 0)
        assert(test_object.vram_temp.reg == 0)
        assert(test_object.write_latch == 0)

    # Test internal registers
    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_control_write(self, test_object, data):
        # Test write to $2000. Verifies the flags of the control register are
        # updated and that the vram_temp.nt_select attribute is updated when a
        # write to $2000 occurs.
        address = 0x2000

        test_object.write(address, data)

        control = test_object.control
        vram = test_object.vram
        vram_temp = test_object.vram_temp
        assert(control.reg == data)
        assert(vram.reg == 0)  # Assert not updated
        assert(control.flags.base_nt_address == (data >> 0) & 3)
        assert(control.flags.vram_address_increment == (data >> 2) & 1)
        assert(control.flags.sprite_pt_address == (data >> 3) & 1)
        assert(control.flags.background_pt_address == (data >> 4) & 1)
        assert(control.flags.sprite_size == (data >> 5) & 1)
        assert(control.flags.ppu_leader_follower_select == (data >> 6) & 1)
        assert(control.flags.generate_nmi == (data >> 7) & 1)
        assert(vram_temp.flags.nt_select == (data >> 0) & 3)

    @pytest.mark.parametrize("data", list(range(0x00, 0xFF)))
    def test_vram_address_write(self, test_object, data):
        # TODO: https://github.com/zeeps31/purenes/issues/28
        # Test writes to $2006. Writing to $2006 requires two writes to set the
        # VRAM address.
        #
        # Verifies on the first write vram_temp is updated correctly and the
        # write_latch is set to 1 and on the second write verifies the internal
        # write_latch is set to 0 and the full address is transferred from
        # t -> v.
        address = 0x2006
        test_object.read(0x2002)  # Init/reset write latch

        vram = test_object.vram
        vram_temp = test_object.vram_temp

        test_object.write(address, data)

        # Verify t: .CDEFGH ........ <- d: ..CDEFGH
        assert(((vram_temp.reg >> 8) & 0x3F) == (data & 0x3F))
        assert(test_object.write_latch == 1)

        test_object.write(address, data)

        # Verify t: ....... ABCDEFGH <- d: ABCDEFGH
        assert(vram.reg == ((data & 0x3F) << 8) | data)
        # Verify v: <...all bits...> <- t: <...all bits...>
        assert(vram.reg == vram_temp.reg)
        assert(test_object.write_latch == 0)

    def test_status_read(self, test_object):
        address = 0x2002

        test_object.read(address)

        assert(test_object.write_latch == 0)

    def test_data_read_x_increment(self, test_object, mock_ppu_bus, mocker):
        # Test PPUDATA $2007 x increment.
        #
        # Test that successive writes to the data register with increment_mode
        # 0 increments the vram address by one byte.
        address = 0x2007

        test_object.read(address)
        test_object.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0001)
        ])

    def test_data_read_y_increment(self, test_object, mock_ppu_bus, mocker):
        # Test PPUDATA $2007 y increment.
        #
        # Test that successive writes to the data register with increment_mode
        # 1 increments the vram address by 32 bytes.
        address = 0x2007

        test_object.write(0x2000, 0x4)

        test_object.read(address)
        test_object.read(address)

        mock_ppu_bus.read.assert_has_calls([
            mocker.call.read(0x0000),
            mocker.call.read(0x0020)
        ])

    def test_data_read_buffer(self, test_object, mock_ppu_bus):
        # Test PPUDATA $2007 read for non-palette address 0-$3EFF.
        #
        # Test that successive reads from $2007 for VVRAM addresses <= $3EFF
        # are buffered and delayed by one frame
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

        assert(actual_values == expected_values)

    def test_data_read_buffer_palette_address(self, test_object, mock_ppu_bus):
        # Tests PPUDATA $2007 read for addresses >= $3F00.
        #
        # Test that successive reads to $2007 for VVRAM addresses >= $3F00
        # are not buffered and returned immediately.
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

        assert(actual_values == expected_values)

import pytest
from purenes.ppu import PPU


class TestPPU(object):

    @pytest.fixture()
    def mock_ppu_bus(self, mocker):
        yield mocker.Mock()

    @pytest.fixture()
    def test_object(self, mock_ppu_bus):
        yield PPU(mock_ppu_bus)

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

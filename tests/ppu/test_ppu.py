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

    def test_status_read(self, test_object):
        address = 0x2002

        test_object.read(address)

        assert(test_object.write_latch == 0)

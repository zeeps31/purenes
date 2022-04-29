import pytest

from purenes.ppu import PPUBus


class TestPPUBus(object):

    INVALID_ADDRESS_EXCEPTION_MESSAGE = ("Invalid address provided: "
                                         "0x10000. Address should "
                                         "be between 0x0000 - 0x3FFF")

    def test_read_from_vram(self, ppu_bus: PPUBus):
        """Test that reads from VRAM for addresses 0x2000-0x2FFF return
        the correct values.
        """
        address_range = [x for x in range(0x2000, 0x2FFF)]

        for address in address_range:
            data: int = ppu_bus.read(address)

            assert data == 0x00

    def test_write_to_vram(self, ppu_bus: PPUBus):
        """Test that writes to VRAM for addresses 0x2000-0x2FFF write the
        correct values to the correct location.
        """
        address_range = [x for x in range(0x2000, 0x2FFF)]
        data = 0x01

        for address in address_range:
            ppu_bus.write(address, data)

            assert ppu_bus.read(address) == data

    def test_read_from_an_incorrect_address_is_invalid(
            self,
            ppu_bus: PPUBus
    ):
        """Test that a read from an address not in the addressable range of the
        PPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            ppu_bus.read(invalid_address)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

    def test_write_to_an_incorrect_address_is_invalid(
            self,
            ppu_bus: PPUBus
    ):
        """Test that writes to an address not in the addressable range of the
        PPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            ppu_bus.write(invalid_address, 0x01)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

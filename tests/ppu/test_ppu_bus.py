import pytest

from purenes import ppu


class TestPPUBus(object):

    INVALID_ADDRESS_EXCEPTION_MESSAGE = ("Invalid address provided: "
                                         "0x10000. Address should "
                                         "be between 0x0000 - 0x3FFF")

    def test_read_from_vram(self, ppu_bus: ppu.PPUBus):
        """Test that reads from VRAM for addresses 0x2000-0x2FFF return
        the correct values.
        """
        address_range = [x for x in range(0x2000, 0x2FFF)]

        for address in address_range:
            data: int = ppu_bus.read(address)

            assert data == 0x00

    def test_read_from_palette_vram(self, ppu_bus: ppu.PPUBus):
        """Tests that reads from palette VRAM for addresses 0x3F00-0x3FFF read
        the correct values from the correct location.
        """
        address_range = [x for x in range(0x3F00, 0x4000)]

        for address in address_range:
            data: int = ppu_bus.read(address)

            assert data == 0x00

    def test_write_to_vram(self, ppu_bus: ppu.PPUBus):
        """Test that writes to VRAM for addresses 0x2000-0x2FFF write the
        correct values to the correct location.
        """
        address_range = [x for x in range(0x2000, 0x2FFF)]
        data = 0x01

        for address in address_range:
            ppu_bus.write(address, data)

            assert ppu_bus.read(address) == data

    def test_write_to_palette_vram(self, ppu_bus: ppu.PPUBus):
        """Tests writes to palette VRAM for addresses 0x3F00-0x3FFF write the
        correct values to the correct location.
        """
        address_range = [x for x in range(0x3F00, 0x4000)]

        for address in address_range:
            data: int = ppu_bus.read(address)

            assert data == 0x00

    def test_palette_reads_mirror_background(self, ppu_bus: ppu.PPUBus):
        """Tests that reads to addresses 0x3F10, 0x3F14, 0x3F18 and 0x3F1C
        return the values stored at 0x3F00, 0x3F04, 0x3F08 and 0x3F0C.
        """
        ppu_bus.write(0x3F00, 0x00)
        ppu_bus.write(0x3F04, 0x01)
        ppu_bus.write(0x3F08, 0x02)
        ppu_bus.write(0x3F0C, 0x03)

        assert ppu_bus.read(0x3F10) == 0x00
        assert ppu_bus.read(0x3F14) == 0x01
        assert ppu_bus.read(0x3F18) == 0x02
        assert ppu_bus.read(0x3F1C) == 0x03

    def test_palette_writes_mirror_background(self, ppu_bus: ppu.PPUBus):
        """Tests writes to addresses 0x3F00, 0x3F04, 0x3F08 and 0x3F0C store
        the values in addresses 0x3F10, 0x3F14, 0x3F18 and 0x3F1C.
        """
        ppu_bus.write(0x3F10, 0x00)
        ppu_bus.write(0x3F14, 0x01)
        ppu_bus.write(0x3F18, 0x02)
        ppu_bus.write(0x3F1C, 0x03)

        assert ppu_bus.read(0x3F00) == 0x00
        assert ppu_bus.read(0x3F04) == 0x01
        assert ppu_bus.read(0x3F08) == 0x02
        assert ppu_bus.read(0x3F0C) == 0x03

    def test_read_from_an_incorrect_address_is_invalid(
            self,
            ppu_bus: ppu.PPUBus
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
            ppu_bus: ppu.PPUBus
    ):
        """Test that writes to an address not in the addressable range of the
        PPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            ppu_bus.write(invalid_address, 0x01)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

import pytest

from purenes.ppu import PPUBus


class TestPPUBus(object):

    INVALID_ADDRESS_EXCEPTION_MESSAGE = ("Invalid address provided: "
                                         "0x10000. Address should "
                                         "be between 0x0000 - 0x3FFF")

    @pytest.fixture()
    def test_object(self):
        ppu_bus: PPUBus = PPUBus()
        yield ppu_bus

    def test_read_from_vram(self, test_object):
        address_range = [x for x in range(0x2000, 0x2FFF)]

        for address in address_range:
            data: int = test_object.read(address)

            assert(data == 0x00)

    def test_write_to_vram(self, test_object):
        address_range = [x for x in range(0x2000, 0x2FFF)]
        data = 0x01

        for address in address_range:
            test_object.write(address, data)

            assert(test_object.read(address) == data)

    def test_read_invalid_address_raises_exception(self, test_object):
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            test_object.read(invalid_address)

        assert(str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE)

    def test_write_invalid_address_raises_exception(self, test_object):
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            test_object.write(invalid_address, 0x01)

        assert(str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE)

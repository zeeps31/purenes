import numpy as np
import pytest

from purenes.cpu import CPUBus


class TestCpuBus(object):

    INVALID_ADDRESS_EXCEPTION_MESSAGE = ("Invalid address provided: "
                                         "0x10000. Address should "
                                         "be between 0x0000 - 0xFFFF")

    @pytest.fixture()
    def test_object(self):
        cpu_bus: CPUBus = CPUBus()
        yield cpu_bus

    def test_read_from_ram(self, test_object):
        address_range = [np.uint16(x) for x in range(0x0000, 0x2000)]

        for address in address_range:
            data: np.uint8 = test_object.read(address)

            assert(data == 0x00)

    def test_write_to_ram(self, test_object):
        address_range = [np.uint16(x) for x in range(0x0000, 0x2000)]
        data = np.uint8(0x01)

        for address in address_range:
            test_object.write(address, data)

            assert(test_object.read(address) == data)

    def test_read_invalid_address_raises_exception(self, test_object):
        invalid_address = np.uint32(0x10000)

        with pytest.raises(Exception) as exception:
            test_object.read(invalid_address)

        assert(str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE)

    def test_write_invalid_address_raises_exception(self, test_object):
        invalid_address = np.uint32(0x10000)

        with pytest.raises(Exception) as exception:
            test_object.write(invalid_address, np.uint8(0x01))

        assert(str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE)

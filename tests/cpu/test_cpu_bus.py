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

    def test_read_from_ram(self, test_object: CPUBus):
        """Test that reads from CPU RAM for addresses 0x0000-0x2000 return
        the correct values.
        """
        address_range = [x for x in range(0x0000, 0x2000)]

        for address in address_range:
            data: int = test_object.read(address)

            assert data == 0x00

    def test_write_to_ram(self, test_object: CPUBus):
        """Test that writes to CPU RAM for addresses 0x0000-0x2000 return
        the correct values.
        """
        address_range = [x for x in range(0x0000, 0x2000)]
        data = 0x01

        for address in address_range:
            test_object.write(address, data)

            assert test_object.read(address) == data

    def test_read_invalid_address_raises_exception(self, test_object: CPUBus):
        """Test that a read from an address not in the addressable range of the
        CPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            test_object.read(invalid_address)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

    def test_write_invalid_address_raises_exception(self, test_object: CPUBus):
        """Test that a write to an address not in the addressable range of the
        CPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            test_object.write(invalid_address, 0x01)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

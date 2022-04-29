import pytest

from purenes.cpu import CPUBus


class TestCpuBus(object):

    INVALID_ADDRESS_EXCEPTION_MESSAGE = ("Invalid address provided: "
                                         "0x10000. Address should "
                                         "be between 0x0000 - 0xFFFF")

    def test_read_from_ram(self, cpu_bus: CPUBus):
        """Test that reads from CPU RAM for addresses 0x0000-0x2000 return
        the correct values.
        """
        address_range = [x for x in range(0x0000, 0x2000)]

        for address in address_range:
            data: int = cpu_bus.read(address)

            assert data == 0x00

    def test_write_to_ram(self, cpu_bus: CPUBus):
        """Test that writes to CPU RAM for addresses 0x0000-0x2000 return
        the correct values.
        """
        address_range = [x for x in range(0x0000, 0x2000)]
        data = 0x01

        for address in address_range:
            cpu_bus.write(address, data)

            assert cpu_bus.read(address) == data

    def test_read_from_an_incorrect_address_is_invalid(
            self,
            cpu_bus: CPUBus
    ):
        """Test that a read from an address not in the addressable range of the
        CPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            cpu_bus.read(invalid_address)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

    def test_write_to_an_incorrect_address_is_invalid(
            self,
            cpu_bus: CPUBus
    ):
        """Test that a write to an address not in the addressable range of the
        CPU throws an exception.
        """
        invalid_address = 0x10000

        with pytest.raises(Exception) as exception:
            cpu_bus.write(invalid_address, 0x01)

        assert str(exception.value) == self.INVALID_ADDRESS_EXCEPTION_MESSAGE

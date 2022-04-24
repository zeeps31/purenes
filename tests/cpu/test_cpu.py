from pytest_mock import MockFixture

from purenes.cpu import CPU


class TestCPU(object):

    def test_clock(self, mocker: MockFixture):
        """Test CPU reset sets the program counter with the values stored at
        the reset vector addresses and the next CPU clock reads from the
        CPUBus using the address stored in the program counter.
        """
        cpu_bus = mocker.Mock()
        cpu_bus.read.side_effect = [
            0x00,  # data at low byte of the reset vector
            0x01,  # data at high byte of the reset vector
            0x00,  # data at program counter
        ]

        test_object = CPU(cpu_bus)
        test_object.reset()

        test_object.clock()

        calls = [
            mocker.call.read(0xFFFC),  # reset vector low byte address
            mocker.call.read(0xFFFD),  # reset vector high byte address
            mocker.call.read(0x0100),  # PC address
        ]
        cpu_bus.assert_has_calls(calls)

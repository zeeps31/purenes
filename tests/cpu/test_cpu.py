from unittest.mock import Mock

from pytest_mock import MockFixture

from purenes.cpu import CPU


class TestCPU(object):

    def test_reset(self, cpu: CPU, mock_cpu_bus: Mock, mocker: MockFixture):
        """Test CPU reset cycle.

        Verifies the program counter is updated with the values stored at
        the reset vector addresses and the next CPU clock reads from the
        CPUBus using the address stored in the program counter. Interrogates
        status and internal registers to ensure the correct values are set
        during reset.
        """
        mock_cpu_bus.read.side_effect = [
            0x00,  # data at low byte of the reset vector
            0x01,  # data at high byte of the reset vector
            0x00,  # data at program counter
        ]

        cpu.reset()

        cpu.clock()

        calls = [
            mocker.call.read(0xFFFC),  # reset vector low byte address
            mocker.call.read(0xFFFD),  # reset vector high byte address
            mocker.call.read(0x0100),  # PC address
        ]
        mock_cpu_bus.assert_has_calls(calls)

        assert cpu.read_only_values["a"] == 0
        assert cpu.read_only_values["x"] == 0
        assert cpu.read_only_values["y"] == 0
        assert cpu.read_only_values["s"] == 0xFD

        assert cpu.status.reg == 0x04
        assert cpu.status.flags.interrupt_disable == 1

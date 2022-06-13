from unittest import mock

import pytest_mock

import purenes.cpu


def test_reset(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture):
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
    ]

    cpu.reset()

    calls = [
        mocker.call.read(0xFFFC),  # reset vector low byte address
        mocker.call.read(0xFFFD),  # reset vector high byte address
    ]
    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.a == 0
    assert cpu.x == 0
    assert cpu.y == 0
    assert cpu.s == 0xFD

    assert cpu.status.reg == 0x04
    assert cpu.status.flags.interrupt_disable == 1

    assert cpu.remaining_cycles == 7

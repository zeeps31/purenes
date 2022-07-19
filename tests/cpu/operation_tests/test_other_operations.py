from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, operation_value, accumulator_value, expected_negative_flag, "
    "expected_overflow_flag, expected_zero_flag, expected_cycle_count",
    [
        (0x24, 0xC0, 0x00, 1, 1, 1, 3),
        (0x2C, 0xC0, 0x00, 1, 1, 1, 4),
        (0x24, 0x80, 0xFF, 1, 0, 0, 3),
        (0x24, 0x40, 0xFF, 0, 1, 0, 3),
        (0x24, 0x00, 0x00, 0, 0, 1, 3),
    ],
    ids=[
        "executes_successfully_using_opcode_0x24",
        "executes_successfully_using_opcode_0x2C",
        "sets_the_negative_flag_correctly",
        "sets_the_overflow_flag_correctly",
        "sets_the_zero_flag_correctly"
    ]
)
def test_BIT(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        accumulator_value: int,
        expected_negative_flag: int,
        expected_overflow_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int):
    """Tests the BIT operation.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The negative flag is set to bit 7 of the operation value.
    3. The overflow flag is set to bit 6 of the operation value.
    4. The zero flag is set if the operation_value & accumulator equal 0.
    3. The operation completes in the correct number of clock cycles.
    """
    cpu.pc = 0x0000
    cpu.a = accumulator_value
    cpu.status.flags.negative = 0
    cpu.status.flags.overflow = 0
    cpu.operation_value = operation_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.remaining_cycles == 0

    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.overflow == expected_overflow_flag
    assert cpu.status.flags.zero == expected_zero_flag


def test_NOP(cpu: purenes.cpu.CPU, mock_cpu_bus: mock.Mock):
    """Tests the NOP operation.

    Verifies the following:

    1. The operation is mapped to the opcode 0xEA.
    2. The operation completes in two clock cycles.
    """
    cpu.pc = 0x0000

    mock_cpu_bus.read.return_value = 0xEA

    for _ in range(0, 2):
        cpu.clock()

    assert cpu.remaining_cycles == 0

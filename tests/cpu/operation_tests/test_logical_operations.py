from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, accumulator_value, operation_value, expected_result, "
    "negative_flag, zero_flag, cycle_count",
    [
        (0x01, 0x00, 0x01, 0x01, 0, 0, 6),
        (0x05, 0x00, 0x01, 0x01, 0, 0, 3),
        (0x09, 0x00, 0x01, 0x01, 0, 0, 2),
        (0x0D, 0x00, 0x01, 0x01, 0, 0, 4),
        (0x15, 0x00, 0x01, 0x01, 0, 0, 4),
        (0x19, 0x00, 0x01, 0x01, 0, 0, 4),
        (0x1D, 0x00, 0x01, 0x01, 0, 0, 4),
        (0x21, 0x01, 0x01, 0x01, 0, 0, 6),
        (0x25, 0x01, 0x01, 0x01, 0, 0, 3),
        (0x29, 0x01, 0x01, 0x01, 0, 0, 2),
        (0x2D, 0x01, 0x01, 0x01, 0, 0, 4),
        (0x31, 0x01, 0x01, 0x01, 0, 0, 5),
        (0x35, 0x01, 0x01, 0x01, 0, 0, 4),
        (0x39, 0x01, 0x01, 0x01, 0, 0, 4),
        (0x3D, 0x01, 0x01, 0x01, 0, 0, 4),
        (0x01, 0x00, 0x00, 0x00, 0, 1, 6),
        (0x01, 0x00, 0x81, 0x81, 1, 0, 6),
    ],
    ids=[
        "executes_successfully_using_opcode_0x01",  # ORA
        "executes_successfully_using_opcode_0x05",  # ORA
        "executes_successfully_using_opcode_0x09",  # ORA
        "executes_successfully_using_opcode_0x0D",  # ORA
        "executes_successfully_using_opcode_0x15",  # ORA
        "executes_successfully_using_opcode_0x19",  # ORA
        "executes_successfully_using_opcode_0x1D",  # ORA
        "executes_successfully_using_opcode_0x21",  # AND
        "executes_successfully_using_opcode_0x25",  # AND
        "executes_successfully_using_opcode_0x29",  # AND
        "executes_successfully_using_opcode_0x2D",  # AND
        "executes_successfully_using_opcode_0x31",  # AND
        "executes_successfully_using_opcode_0x35",  # AND
        "executes_successfully_using_opcode_0x39",  # AND
        "executes_successfully_using_opcode_0x3D",  # AND
        "sets_the_zero_flag_when_the_result_is_zero",
        "sets_the_negative_flag_if_the_result_exceeds_the_signed_8_bit_maximum"
    ]
)
def test_logical_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int,
        operation_value: int,
        expected_result: int,
        negative_flag: int,
        zero_flag: int,
        cycle_count: int
):
    """Tests logical operations (AND, EOR, ORA).

    Clocks the CPU and verifies that the following actions are performed during
    the ORA operation.

    1. The operation is mapped to the correct opcode.
    2. The result of performing the logical operation on the accumulator is the
       expected result.
    3. The negative (N) flag is set under the correct conditions.
    4. The zero (Z) flag is set under the correct conditions.
    """
    cpu.pc = 0x0000
    cpu.a = accumulator_value
    cpu.operation_value = operation_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.a == expected_result
    assert cpu.status.flags.negative == negative_flag
    assert cpu.status.flags.zero == zero_flag
    assert cpu.remaining_cycles == 0

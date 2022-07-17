from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, accumulator_value, operation_value, expected_result, "
    "expected_negative_flag, expected_zero_flag, expected_cycle_count",
    [  # OP    A     OV    ER    EN EZ EC
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
        (0x41, 0x01, 0x02, 0x03, 0, 0, 6),
        (0x45, 0x01, 0x02, 0x03, 0, 0, 3),
        (0x49, 0x01, 0x02, 0x03, 0, 0, 2),
        (0x4D, 0x01, 0x02, 0x03, 0, 0, 4),
        (0x51, 0x01, 0x02, 0x03, 0, 0, 5),
        (0x55, 0x01, 0x02, 0x03, 0, 0, 4),
        (0x59, 0x01, 0x02, 0x03, 0, 0, 4),
        (0x5D, 0x01, 0x02, 0x03, 0, 0, 4),
        (0x01, 0x00, 0x00, 0x00, 0, 1, 6),
        (0x01, 0x00, 0x81, 0x81, 1, 0, 6),
        (0x41, 0x01, 0x01, 0x00, 0, 1, 6),
        (0x41, 0x00, 0x80, 0x80, 1, 0, 6),
    ],
    ids=[
        "ORA_executes_successfully_using_opcode_0x01",  # ORA
        "ORA_executes_successfully_using_opcode_0x05",  # ORA
        "ORA_executes_successfully_using_opcode_0x09",  # ORA
        "ORA_executes_successfully_using_opcode_0x0D",  # ORA
        "ORA_executes_successfully_using_opcode_0x15",  # ORA
        "ORA_executes_successfully_using_opcode_0x19",  # ORA
        "ORA_executes_successfully_using_opcode_0x1D",  # ORA
        "AND_executes_successfully_using_opcode_0x21",  # AND
        "AND_executes_successfully_using_opcode_0x25",  # AND
        "AND_executes_successfully_using_opcode_0x29",  # AND
        "AND_executes_successfully_using_opcode_0x2D",  # AND
        "AND_executes_successfully_using_opcode_0x31",  # AND
        "AND_executes_successfully_using_opcode_0x35",  # AND
        "AND_executes_successfully_using_opcode_0x39",  # AND
        "AND_executes_successfully_using_opcode_0x3D",  # AND
        "EOR_executes_successfully_using_opcode_0x41",  # EOR
        "EOR_executes_successfully_using_opcode_0x45",  # EOR
        "EOR_executes_successfully_using_opcode_0x49",  # EOR
        "EOR_executes_successfully_using_opcode_0x4D",  # EOR
        "EOR_executes_successfully_using_opcode_0x51",  # EOR
        "EOR_executes_successfully_using_opcode_0x55",  # EOR
        "EOR_executes_successfully_using_opcode_0x59",  # EOR
        "EOR_executes_successfully_using_opcode_0x5D",  # EOR
        "ORA_sets_the_zero_flag_correctly",
        "ORA_sets_the_negative_flag_correctly",
        "EOR_sets_the_zero_flag_correctly",
        "EOR_sets_the_negative_flag_correctly"
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
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int
):
    """Tests logical operations (AND, EOR, ORA).

    Verifies the following.

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

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.a == expected_result
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.remaining_cycles == 0

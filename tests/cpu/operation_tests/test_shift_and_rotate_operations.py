from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    ("opcode, operation_value, effective_address, carry_flag, "
     "expected_result, expected_carry_flag, expected_negative_flag, "
     "expected_zero_flag, expected_cycle_count"),
    [  # OP    OV    EA      C  ER   EC EN EZ EC
        (0x06, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 5),
        (0x0E, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 6),
        (0x16, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 6),
        (0x1E, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 7),
        (0x26, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 5),
        (0x2E, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 6),
        (0x36, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 6),
        (0x3E, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 7),
        (0x46, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 5),
        (0x4E, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 6),
        (0x56, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 6),
        (0x5E, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 7),
        (0x66, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 5),
        (0x6E, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 6),
        (0x76, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 6),
        (0x7E, 0x81, 0x0000, 0, 0x40, 1, 0, 0, 7),
        (0x06, 0x81, 0x0000, 0, 0x02, 1, 0, 0, 5),
        (0x06, 0xFF, 0x0000, 0, 0xFE, 1, 1, 0, 5),
        (0x06, 0x00, 0x0000, 0, 0x00, 0, 0, 1, 5),
        (0x26, 0x81, 0x0000, 0, 0x02, 1, 0, 0, 5),
        (0x26, 0x40, 0x0000, 0, 0x80, 0, 1, 0, 5),
        (0x26, 0x00, 0x0000, 0, 0x00, 0, 0, 1, 5),
        (0x46, 0x80, 0x0000, 0, 0x40, 0, 0, 0, 5),
        (0x46, 0x01, 0x0000, 0, 0x00, 1, 0, 1, 5),
        (0x66, 0x03, 0x0000, 0, 0x01, 1, 0, 0, 5),
        (0x66, 0x80, 0x0000, 1, 0xC0, 0, 1, 0, 5),
        (0x66, 0x00, 0x0000, 0, 0x00, 0, 0, 1, 5),
    ],
    ids=[
        "ASL_executes_successfully_using_opcode_0x06",
        "ASL_executes_successfully_using_opcode_0x0E",
        "ASL_executes_successfully_using_opcode_0x16",
        "ASL_executes_successfully_using_opcode_0x1E",
        "ROL_executes_successfully_using_opcode_0x26",
        "ROL_executes_successfully_using_opcode_0x2E",
        "ROL_executes_successfully_using_opcode_0x36",
        "ROL_executes_successfully_using_opcode_0x3E",
        "LSR_executes_successfully_using_opcode_0x46",
        "LSR_executes_successfully_using_opcode_0x4E",
        "LSR_executes_successfully_using_opcode_0x56",
        "LSR_executes_successfully_using_opcode_0x5E",
        "ROR_executes_successfully_using_opcode_0x66",
        "ROR_executes_successfully_using_opcode_0x6E",
        "ROR_executes_successfully_using_opcode_0x76",
        "ROR_executes_successfully_using_opcode_0x7E",
        "ASL_sets_the_carry_flag_under_the_correct_conditions",
        "ASL_sets_the_negative_flag_under_the_correct_conditions",
        "ASL_sets_the_zero_flag_under_the_correct_conditions",
        "ROL_sets_the_carry_flag_under_the_correct_conditions",
        "ROL_sets_the_negative_flag_under_the_correct_conditions",
        "ROL_sets_the_zero_flag_under_the_correct_conditions",
        "LSR_sets_the_carry_flag_under_the_correct_conditions",
        "LSR_sets_the_zero_flag_under_the_correct_conditions",
        "ROR_sets_the_carry_flag_under_the_correct_conditions",
        "ROR_sets_the_negative_flag_under_the_correct_conditions",
        "ROR_sets_the_zero_flag_under_the_correct_conditions",
    ]
)
def test_shift_and_rotate_instructions(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        effective_address: int,
        carry_flag: int,
        expected_result: int,
        expected_carry_flag: int,
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int):
    """Tests shift and rotate operations.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. All bits in the operation value are shifted or rotated as expected and
       written back to the effective address.
    3. The carry flag is set under the correct conditions.
    4. The negative flag is set under the correct conditions.
    5. For results that are zero, verifies the zero flag is set.
    6. The operation completes in the correct number of clock cycles.
    """
    cpu.pc = 0x0000
    cpu.status.flags.carry = carry_flag
    cpu.operation_value = operation_value
    cpu.effective_address = effective_address

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    calls = [
        mocker.call.write(effective_address, expected_result)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.flags.carry == expected_carry_flag
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.remaining_cycles == 0


@pytest.mark.parametrize(
    ("opcode, accumulator_value, carry_flag, expected_result, "
     "expected_carry_flag, expected_negative_flag, expected_zero_flag, "
     "expected_cycle_count"),
    [  # OP    A     C  ER   EC EN EZ EC
        (0x0A, 0x10, 0, 0x20, 0, 0, 0, 2),
        (0x2A, 0x80, 1, 0x01, 1, 0, 0, 2),
        (0x4A, 0x81, 0, 0x40, 1, 0, 0, 2),
        (0x6A, 0x81, 0, 0x40, 1, 0, 0, 2),
    ],
    ids=[
        "ASL_executes_successfully_using_opcode_0x0A",
        "ROL_executes_successfully_using_opcode_0x2A",
        "LSR_executes_successfully_using_opcode_0x4A",
        "ROR_executes_successfully_using_opcode_0x6A",
    ]
)
def test_shift_and_rotate_instructions_with_accumulator_addressing(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int,
        carry_flag: int,
        expected_result: int,
        expected_carry_flag: int,
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int
):
    """Tests shift and rotate instructions that using accumulator addressing.

    Placed in a separate test as the verification steps required warrant a
    separate test.

    Verifies the following:

    1. The accumulator is set to the operation value with the correct bit
       shifted in (left or right)
    2. The operation completes in the correct number of clock cycles.
    """
    cpu.pc = 0x0000
    cpu.a = accumulator_value
    cpu.status.flags.carry = carry_flag
    cpu.operation_value = accumulator_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.a == expected_result
    assert cpu.status.flags.carry == expected_carry_flag
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.remaining_cycles == 0

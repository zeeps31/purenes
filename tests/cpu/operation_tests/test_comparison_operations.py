from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, operation_value, accumulator_value, x_value, y_value, "
    "expected_carry_flag, expected_zero_flag, expected_negative_flag, "
    "expected_cycle_count",
    [  # OP    OV    A     X     Y    EC EZ EN ECC
        (0xC0, 0x01, 0x00, 0x00, 0x02, 1, 0, 0, 2),  # CPY
        (0xC1, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 6),  # CMP
        (0xC4, 0x01, 0x00, 0x00, 0x02, 1, 0, 0, 3),  # CPY
        (0xC5, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 3),  # CMP
        (0xC9, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 2),  # CMP
        (0xCC, 0x01, 0x00, 0x00, 0x02, 1, 0, 0, 4),  # CPY
        (0xCD, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 4),  # CMP
        (0xD1, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 5),  # CMP
        (0xD5, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 4),  # CMP
        (0xD9, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 4),  # CMP
        (0xDD, 0x01, 0x02, 0x00, 0x00, 1, 0, 0, 4),  # CMP
        (0xE0, 0x01, 0x00, 0x02, 0x00, 1, 0, 0, 2),  # CPX
        (0xE4, 0x01, 0x00, 0x02, 0x00, 1, 0, 0, 3),  # CPX
        (0xEC, 0x01, 0x00, 0x02, 0x00, 1, 0, 0, 4),  # CPX
        (0xC1, 0x02, 0x00, 0x00, 0x00, 0, 0, 1, 6),  # CMP
        (0xC1, 0x01, 0x81, 0x00, 0x00, 1, 0, 1, 6),  # CMP
        (0xC1, 0x00, 0x00, 0x00, 0x00, 1, 1, 0, 6),  # CMP
        (0xE0, 0x02, 0x00, 0x00, 0x00, 0, 0, 1, 2),  # CPX
        (0xE0, 0x01, 0x00, 0x81, 0x00, 1, 0, 1, 2),  # CPX
        (0xE0, 0x00, 0x00, 0x00, 0x00, 1, 1, 0, 2),  # CPX
        (0xC0, 0x02, 0x00, 0x00, 0x00, 0, 0, 1, 2),  # CPY
        (0xC0, 0x01, 0x00, 0x00, 0x81, 1, 0, 1, 2),  # CPY
        (0xC0, 0x00, 0x00, 0x00, 0x00, 1, 1, 0, 2),  # CPY
    ],
    ids=[
        "CPY_executes_successfully_using_opcode_0xC0",
        "CMP_executes_successfully_using_opcode_0xC1",
        "CPY_executes_successfully_using_opcode_0xC4",
        "CMP_executes_successfully_using_opcode_0xC5",
        "CMP_executes_successfully_using_opcode_0xC9",
        "CPY_executes_successfully_using_opcode_0xCC",
        "CMP_executes_successfully_using_opcode_0xCD",
        "CMP_executes_successfully_using_opcode_0xD1",
        "CMP_executes_successfully_using_opcode_0xD5",
        "CMP_executes_successfully_using_opcode_0xD9",
        "CMP_executes_successfully_using_opcode_0xDD",
        "CPX_executes_successfully_using_opcode_0xE0",
        "CPX_executes_successfully_using_opcode_0xE4",
        "CPX_executes_successfully_using_opcode_0xEC",
        "CMP_sets_C_Z_N_flags_correctly_for_LT_conditions",
        "CMP_sets_C_Z_N_flags_correctly_for_GT_conditions",
        "CMP_sets_C_Z_N_flags_correctly_for_EQ_conditions",
        "CPX_sets_C_Z_N_flags_correctly_for_LT_conditions",
        "CPX_sets_C_Z_N_flags_correctly_for_GT_conditions",
        "CPX_sets_C_Z_N_flags_correctly_for_EQ_conditions",
        "CPY_sets_C_Z_N_flags_correctly_for_LT_conditions",
        "CPY_sets_C_Z_N_flags_correctly_for_GT_conditions",
        "CPY_sets_C_Z_N_flags_correctly_for_EQ_conditions",
    ]
)
def test_comparison_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        accumulator_value: int,
        x_value: int,
        y_value: int,
        expected_carry_flag: int,
        expected_zero_flag: int,
        expected_negative_flag: int,
        expected_cycle_count: int,
):
    """Tests comparison instructions.

    Common test for all comparison instructions.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation sets the flags appropriately for the conditions shown
       below:

        description                 Z	C	N
        ------------------------------------------------------
        register < operation_value	0	0	sign bit of result
        register = operation_value	1	1	0
        register > operation_value	0	1	sign bit of result

    3. The operation completes in the correct number of clock cycles.

    """
    cpu.effective_address = 0x0000
    cpu.operation_value = operation_value
    cpu.pc = 0x0000

    cpu.a = accumulator_value
    cpu.x = x_value
    cpu.y = y_value

    cpu.status.flags.carry = 0
    cpu.status.flags.zero = 0
    cpu.status.flags.negative = 0

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.status.flags.carry == expected_carry_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.status.flags.negative == expected_negative_flag

    assert cpu.remaining_cycles == 0

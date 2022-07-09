from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, operation_value, effective_address, program_counter, carry_flag, "
    "zero_flag, negative_flag, overflow_flag, cycle_count",
    [
        (0x10, 0x10, 0x0011, 0x0011, 0, 0, 0, 0, 3),  # BPL
        (0x30, 0x10, 0x0011, 0x0011, 0, 0, 1, 0, 3),  # BMI
        (0x50, 0x10, 0x0011, 0x0011, 0, 0, 0, 0, 3),  # BVC
        (0x70, 0x10, 0x0011, 0x0011, 0, 0, 0, 1, 3),  # BVS
        (0x90, 0x10, 0x0011, 0x0011, 0, 0, 0, 0, 3),  # BCC
        (0xB0, 0x10, 0x0011, 0x0011, 1, 0, 0, 0, 3),  # BCS
        (0xD0, 0x10, 0x0011, 0x0011, 0, 0, 0, 0, 3),  # BNE
        (0xF0, 0x10, 0x0011, 0x0011, 0, 1, 0, 0, 3),  # BEQ
        (0x10, 0xFF, 0x0100, 0x0100, 0, 0, 0, 0, 4),
        (0x10, 0x10, 0x0000, 0x0001, 0, 0, 1, 0, 2),
    ],
    ids=[
        "executes_BPL_if_negative_flag_is_zero",
        "executes_BMI_if_negative_flag_is_one",
        "executes_BVC_if_overflow_flag_is_zero",
        "executes_BVS_if_overflow_flag_is_one",
        "executes_BCC_if_carry_flag_is_zero",
        "executes_BCS_if_carry_flag_is_one",
        "executes_BNE_if_zero_flag_is_zero",
        "executes_BEQ_if_zero_flag_is_one",
        "adds_a_cycle_if_a_page_is_crossed",
        "does_not_add_cycles_if_branch_condition_is_not_met"
    ]
)
def test_branching_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        effective_address: int,
        program_counter,
        carry_flag: int,
        zero_flag: int,
        negative_flag: int,
        overflow_flag: int,
        cycle_count: int,
):
    """Tests branching instructions.

    Common test for all branching instructions.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation completes in two cycles if the branching condition is not
       met.
    3. Adds a cycle if the branching condition is met.
    4. Correctly updates the program counter by adding the value of the current
       operation value, if the branching condition is met.
    5. Adds an extra cycle if a page is crossed.
    """
    cpu.effective_address = 0x0000
    cpu.pc = 0x0000

    cpu.status.flags.carry = carry_flag
    cpu.status.flags.zero = zero_flag
    cpu.status.flags.negative = negative_flag
    cpu.status.flags.overflow = overflow_flag
    cpu.operation_value = operation_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.remaining_cycles == 0
    assert cpu.effective_address == effective_address  # Expected address
    assert cpu.pc == program_counter  # Expected program counter

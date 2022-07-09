from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, carry_flag, interrupt_disable_flag, overflow_flag, decimal_flag, "
    "cycle_count",
    [
        (0x18, 1, 0, 0, 0, 2),  # CLC
        (0x58, 0, 1, 0, 0, 2),  # CLI
        (0xB8, 0, 0, 1, 0, 2),  # CLV
        (0xD8, 0, 0, 0, 1, 2),  # CLD
    ],
    ids=[
        "clears_carry_flag",
        "clears_interrupt_disable_flag",
        "clears_overflow_flag",
        "clears_decimal_flag"
    ]
)
def test_flag_clear_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        carry_flag: int,
        interrupt_disable_flag: int,
        overflow_flag: int,
        decimal_flag: int,
        cycle_count: int):
    """Tests clear flag instructions.

    Common test for all operations that clear flags.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The flag under test is set to 0 after performing the operation.
    3. The operation completes in two clock cycles.
    """
    cpu.effective_address = 0x0000
    cpu.pc = 0x0000

    cpu.status.flags.carry = carry_flag
    cpu.status.flags.interrupt_disable = interrupt_disable_flag
    cpu.status.flags.overflow = overflow_flag
    cpu.status.flags.decimal = decimal_flag

    mocker.patch.object(cpu, "_retrieve_operation_value")
    mock_cpu_bus.read.return_value = opcode

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.remaining_cycles == 0
    assert cpu.status.flags.carry == 0
    assert cpu.status.flags.interrupt_disable == 0
    assert cpu.status.flags.overflow == 0
    assert cpu.status.flags.decimal == 0


@pytest.mark.parametrize(
    "opcode, carry_flag, interrupt_disable_flag, decimal_flag, cycle_count",
    [
        (0x38, 0, 1, 1, 2),  # SEC
        (0x78, 1, 0, 1, 2),  # SEI
        (0xF8, 1, 1, 0, 2),  # SED
    ],
    ids=[
        "sets_carry_flag",
        "sets_interrupt_disable_flag",
        "sets_decimal_flag"
    ]
)
def test_flag_set_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        carry_flag: int,
        interrupt_disable_flag: int,
        decimal_flag: int,
        cycle_count: int):
    """Tests set flag instructions.

    Common test for all operations that set flags.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The flag under test is set to 1 after performing the operation.
    3. The operation completes in two clock cycles.
    """
    cpu.effective_address = 0x0000
    cpu.pc = 0x0000

    cpu.status.flags.carry = carry_flag
    cpu.status.flags.interrupt_disable = interrupt_disable_flag
    cpu.status.flags.decimal = decimal_flag

    mocker.patch.object(cpu, "_retrieve_operation_value")
    mock_cpu_bus.read.return_value = opcode

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.remaining_cycles == 0

    assert cpu.status.flags.carry == 1
    assert cpu.status.flags.interrupt_disable == 1
    assert cpu.status.flags.decimal == 1

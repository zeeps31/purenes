from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    ("opcode, operation_value, effective_address, carry_flag, "
     "expected_result, expected_carry_flag, expected_negative_flag, "
     "expected_zero_flag, expected_cycle_count"),
    [
        (0x06, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 5),
        (0x0E, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 6),
        (0x16, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 6),
        (0x1E, 0x10, 0x0000, 0, 0x20, 0, 0, 0, 7),
        (0x26, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 5),
        (0x2E, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 6),
        (0x36, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 6),
        (0x3E, 0x80, 0x0000, 1, 0x01, 1, 0, 0, 7),
        (0x06, 0x81, 0x0000, 0, 0x02, 1, 0, 0, 5),
        (0x06, 0xFF, 0x0000, 0, 0xFE, 1, 1, 0, 5),
        (0x06, 0x00, 0x0000, 0, 0x00, 0, 0, 1, 5),
        (0x26, 0x81, 0x0000, 0, 0x02, 1, 0, 0, 5),
        (0x26, 0x40, 0x0000, 0, 0x80, 0, 1, 0, 5),
        (0x26, 0x00, 0x0000, 0, 0x00, 0, 0, 1, 5),
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
        "ASL_sets_the_carry_flag_under_the_correct_conditions",
        "ASL_sets_the_negative_flag_under_the_correct_conditions",
        "ASL_sets_the_zero_flag_under_the_correct_conditions",
        "ROL_sets_the_carry_flag_under_the_correct_conditions",
        "ROL_sets_the_negative_flag_under_the_correct_conditions",
        "ROL_sets_the_zero_flag_under_the_correct_conditions",
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
    [
        (0x0A, 0x10, 0, 0x20, 0, 0, 0, 2),
        (0x2A, 0x80, 1, 0x01, 1, 0, 0, 2),
    ],
    ids=[
        "ASL_executes_successfully_using_opcode_0x0A",
        "ROL_executes_successfully_using_opcode_0x2A",
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


@pytest.mark.parametrize(
    "opcode, effective_address, x_value, y_value, accumulator_value, "
    "expected_value, expected_cycle_count",
    [
        (0x81, 0x0000, 0x00, 0x00, 0x01, 0x01, 6),  # STA
        (0x84, 0x0000, 0x00, 0x01, 0x00, 0x01, 3),  # STY
        (0x85, 0x0000, 0x00, 0x00, 0x01, 0x01, 3),  # STA
        (0x8C, 0x0000, 0x00, 0x01, 0x00, 0x01, 4),  # STY
        (0x8D, 0x0000, 0x00, 0x00, 0x01, 0x01, 4),  # STA
        (0x91, 0x0000, 0x00, 0x00, 0x01, 0x01, 6),  # STA
        (0x94, 0x0000, 0x00, 0x01, 0x00, 0x01, 4),  # STY
        (0x95, 0x0000, 0x00, 0x00, 0x01, 0x01, 4),  # STA
        (0x96, 0x0000, 0x01, 0x00, 0x00, 0x01, 4),  # STX
        (0x99, 0x0000, 0x00, 0x00, 0x01, 0x01, 5),  # STA
        (0x9D, 0x0000, 0x00, 0x00, 0x01, 0x01, 5),  # STA
    ],
    ids=[
        "STA_executes_successfully_using_opcode_0x81",
        "STY_executes_successfully_using_opcode_0x84",
        "STA_executes_successfully_using_opcode_0x85",
        "STY_executes_successfully_using_opcode_0x8C",
        "STA_executes_successfully_using_opcode_0x8D",
        "STA_executes_successfully_using_opcode_0x91",
        "STY_executes_successfully_using_opcode_0x94",
        "STA_executes_successfully_using_opcode_0x95",
        "STX_executes_successfully_using_opcode_0x96",
        "STA_executes_successfully_using_opcode_0x99",
        "STA_executes_successfully_using_opcode_0x9D",
    ]
)
def test_store_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        effective_address: int,
        x_value: int,
        y_value: int,
        accumulator_value: int,
        expected_value: int,
        expected_cycle_count: int):
    """Test store instructions.

    Common test for all store instructions. The individual values for registers
    are provided as parameters and validated against the "expected_value"
    parameter.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation writes the value being stored to the effective address.
    3. The operation completes in the expected number of clock cycles.
    """
    cpu.effective_address = 0x0000
    cpu.pc = 0x0000
    cpu.x = x_value
    cpu.y = y_value
    cpu.a = accumulator_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    calls = [
        mocker.call.write(effective_address, expected_value)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.remaining_cycles == 0


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


@pytest.mark.parametrize(
    "opcode, effective_address, program_counter, cycle_count",
    [
        (0x6C, 0x0001, 0x0000, 5),
    ],
    ids=[
        "executes_successfully_using_opcode_0x6C",
    ]
)
def test_JMP(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        effective_address: int,
        program_counter: int,
        cycle_count: int):
    """Tests the JMP operation.

    The JMP operation has only one opcode 0x6C.

    Verifies the following:

    1. The JMP operation is mapped to opcode 0x6C.
    2. The program counter is set to the effective_address.
    3. The operation completes in 5 clock cycles.
    """
    cpu.pc = program_counter
    cpu.effective_address = effective_address

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.remaining_cycles == 0
    assert cpu.pc == effective_address


def test_BRK(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture):
    """Tests the BRK operation using opcode 0x00.

    Clocks the CPU and verifies the following actions are performed during the
    BRK operation:

    1. The interrupt and brk flags of the status register are set to 1.
    2. The high and low bytes are of the program counter pushed to the stack
       (in this order).
    3. The value of the status register is pushed to the stack.
    4. The program counter is set to the value of the high and low bytes stored
       at the IRQ vector addresses.
    """
    cpu.pc = 0x0000
    cpu.status.reg = 0x00
    cpu.s = 0xFD

    mock_cpu_bus.read.side_effect = [
        0x00,  # data at program counter address (BRK operation)
        0x01,  # dummy data at low address of the interrupt vector
        0x01,  # dummy data at high address of the interrupt vector
    ]

    for _ in range(0, 7):
        cpu.clock()

    calls = [
        mocker.call.read(0x0000),         # PC address
        # Stack writes
        mocker.call.write(0x01FD, 0x00),  # PC high byte pushed to stack
        mocker.call.write(0x01FC, 0x02),  # PC low byte pushed to stack
        mocker.call.write(0x01FB, 0x14),  # Status reg pushed to stack
        # IRQ vector reads
        mocker.call.read(0xFFFE),         # Interrupt vector low byte address
        mocker.call.read(0xFFFF),         # Interrupt vector high byte address
    ]

    mock_cpu_bus.assert_has_calls(calls)

    # The program counter is set to the value at the IRQ vector
    assert cpu.pc == 0x0101

    # 3 values are pushed to the stack during this operation. The stack pointer
    # should be decremented by 3 (0xFD-3)
    assert cpu.s == 0xFA

    assert cpu.status.flags.brk == 1
    assert cpu.status.flags.interrupt_disable == 1
    assert cpu.status.reg == 0x14
    assert cpu.remaining_cycles == 0


@pytest.mark.parametrize(
    "program_counter, effective_address, cycle_count",
    [
        (0x0000, 0x0001, 6),
        (0x00FF, 0x0200, 6),
    ],
    ids=[
        "executes_successfully_using_opcode_0x20",
        "writes_program_counter_to_stack_low_to_high",
    ]
)
def test_JSR(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        program_counter: int,
        effective_address: int,
        cycle_count: int):
    """Tests the JSR operation.

    Verifies the following:

    1. The JSR operation is mapped to opcode 0x20.
    2. The program counter pushed to the stack is decremented by one.
    3. The program counter is pushed to the stack in order of high to low
       bytes.
    4. The stack pointer is decremented by two.
    5. The program counter is equal to the effective address after the
       operation is performed.
    6. The operation takes 6 clock cycles to complete.
    """
    cpu.pc = program_counter
    cpu.s = 0xFD
    cpu.effective_address = effective_address

    opcode: int = 0x20  # Only one opcode for this operation

    mocker.patch.object(cpu, "_retrieve_operation_value")

    mock_cpu_bus.read.side_effect = [
        opcode
    ]

    for _ in range(0, cycle_count):
        cpu.clock()

    calls = [
        mocker.call.read(program_counter),
        # PC is expected to be decremented by 1
        mocker.call.write(0x01FD, program_counter & 0xFF00),  # PC high byte
        mocker.call.write(0x01FC, program_counter & 0x00FF),  # PC low byte
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.s == 0xFB  # Stack pointer decremented by two
    assert cpu.remaining_cycles == 0
    assert cpu.pc == effective_address


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


def test_PHP(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture):
    """Tests PHP (Push Processor Status on Stack) operation using opcode 0x08.

    Clocks the CPU and verifies that the following actions are performed during
    the PHP operation.

    1. The value of the status register (P) is pushed to the stack with the brk
       flag set.
    2. The stack pointer is decremented by one.
    3. The brk flag is reset to 0 after it is pushed.
    """
    cpu.pc = 0x0000
    cpu.s = 0xFD
    cpu.status.reg = 0x00

    mock_cpu_bus.read.return_value = 0x08  # Opcode

    for _ in range(0, 3):
        cpu.clock()

    calls = [
        mocker.call.write(0x01FD, 0x10)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.reg == 0x00
    assert cpu.s == 0xFC
    assert cpu.remaining_cycles == 0

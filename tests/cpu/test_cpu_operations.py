from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    ("opcode, operation_value, effective_address, carry_flag, negative_flag, "
     "zero_flag, cycle_count"),
    [
        (0x06, 0x10, 0x0000, 0, 0, 0, 5),
        (0x0E, 0x10, 0x0000, 0, 0, 0, 6),
        (0x06, 0x81, 0x0000, 1, 0, 0, 5),
        (0x06, 0xFF, 0x0000, 1, 1, 0, 5),
        (0x06, 0x00, 0x0000, 0, 0, 1, 5),
    ],
    ids=[
        "executes_successfully_using_opcode_0x06",
        "executes_successfully_using_opcode_0x0E",
        "sets_the_carry_flag_under_the_correct_conditions",
        "sets_the_negative_flag_under_the_correct_conditions",
        "sets_the_zero_flag_under_the_correct_conditions",
    ]
)
def test_ASL(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        effective_address: int,
        carry_flag: int,
        negative_flag: int,
        zero_flag: int,
        cycle_count: int,
):
    """Tests the ASL (Arithmetic Shift Left) operation.

    Clocks the CPU and verifies that the following actions are performed during
    the ASL operation.

    1. The operation is mapped to the correct opcode.
    2. All bits in the operation value are shifted left by one bit and written
       back to the effective address.
    3. For operation values where bit 7 is 1, verifies that the value of bit
       7 is shifted into the carry flag.
    4. For results where bit 7 is 1 after the operation is performed, verifies
       that the negative flag is set.
    5. For results that are zero, verifies the zero flag is set.
    """
    cpu.pc = 0x0000
    cpu.operation_value = operation_value
    cpu.effective_address = effective_address

    mock_cpu_bus.read.return_value = opcode # Opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, cycle_count):
        cpu.clock()

    calls = [
        mocker.call.write(0x0000, (operation_value << 1) & 0x00FF)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.flags.carry == carry_flag
    assert cpu.status.flags.negative == negative_flag
    assert cpu.status.flags.zero == zero_flag
    assert cpu.remaining_cycles == 0


def test_ASL_with_accumulator_addressing(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture
):
    """Tests the ASL (Arithmetic Shift Left) operation using accumulator
    addressing (opcode 0x0A).

    Placed in a separate test as the verification steps required warrant a
    separate test.

    Verifies the following:

    1. The accumulator is set to the operation value with a zero bit shifted in
       on the right.
    2. The operation takes two clock cycles to complete.
    """
    cpu.pc = 0x0000
    cpu.a = 0x00
    cpu.operation_value = 0x10

    mock_cpu_bus.read.return_value = 0x0A  # Opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, 2):
        cpu.clock()

    assert cpu.a == 0x20
    assert cpu.operation_value == 0x20
    assert cpu.remaining_cycles == 0


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
    "opcode, accumulator_value, operation_value, negative_flag, zero_flag, "
    "cycle_count",
    [
        (0x01, 0x00, 0x01, 0, 0, 6),
        (0x05, 0x00, 0x01, 0, 0, 3),
        (0x09, 0x00, 0x01, 0, 0, 2),
        (0x0D, 0x00, 0x01, 0, 0, 4),
        (0x01, 0x00, 0x00, 0, 1, 6),
        (0x01, 0x00, 0x81, 1, 0, 6),
    ],
    ids=[
        "executes_successfully_using_opcode_0x01",
        "executes_successfully_using_opcode_0x05",
        "executes_successfully_using_opcode_0x09",
        "executes_successfully_using_opcode_0x0D",
        "sets_the_zero_flag_when_the_result_is_zero",
        "sets_the_negative_flag_if_the_result_exceeds_the_signed_8_bit_maximum"
    ]
)
def test_ORA(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int,
        operation_value: int,
        negative_flag: int,
        zero_flag: int,
        cycle_count: int
):
    """Tests the ORA (Or with Accumulator) operation.

    Clocks the CPU and verifies that the following actions are performed during
    the ORA operation.

    1. The operation is mapped to the correct opcode.
    2. The accumulator register is correctly ORed with the operation value.
    3. The negative (N) flag is set under the correct conditions.
    4. The zero (Z) flag is set under the correct conditions.
    """
    cpu.pc = 0x0000
    cpu.a = accumulator_value
    cpu.operation_value = operation_value

    mock_cpu_bus.read.return_value = opcode  # Opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, cycle_count):
        cpu.clock()

    assert cpu.a == accumulator_value | operation_value
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

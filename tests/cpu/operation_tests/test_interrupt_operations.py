from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


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
    "status_register, pc_lo, pc_hi, stack_pointer, "
    "expected_status_register_address, expected_pc_lo_address, "
    "expected_pc_hi_address, expected_status_register, "
    "expected_program_counter, expected_stack_pointer",
    [  # SR    PL    PH    SP    ESRA    EPLA    EPHI    ESR   EPC     ESP
        (0x00, 0x00, 0x00, 0xFA, 0x01FA, 0x01FB, 0x01FC, 0x00, 0x0000, 0xFD),
        (0xFF, 0x00, 0x00, 0xFA, 0x01FA, 0x01FB, 0x01FC, 0xFF, 0x0000, 0xFD),
        (0x00, 0xFF, 0xFF, 0xFA, 0x01FA, 0x01FB, 0x01FC, 0x00, 0xFFFF, 0xFD),
    ],
    ids=[
        "executes_successfully_using_opcode_0x40",
        "sets_the_status_register_correctly",
        "sets_the_program_counter_correctly",
    ]
)
def test_RTI(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        status_register: int,
        pc_lo: int,
        pc_hi: int,
        stack_pointer: int,
        expected_status_register_address: int,
        expected_pc_lo_address: int,
        expected_pc_hi_address: int,
        expected_status_register: int,
        expected_program_counter: int,
        expected_stack_pointer: int):
    """Tests the RTI operation.

    Verifies the following:

    1. The operation is mapped to opcode 0x40.
    2. The operation pulls the status register from the stack and sets it.
    3. The program counter is pulled from the stack in order of low to high
       bytes
    4. The program counter is set to the program counter pulled from the stack.
    5. The stack pointer is incremented correctly.
    6. The operation completes in 6 clock cycles.
    """
    cpu.pc = 0x0000
    cpu.s = stack_pointer

    mock_cpu_bus.read.side_effect = [
        0x40,  # opcode
        status_register,
        pc_lo,
        pc_hi,
    ]

    for _ in range(0, 6):
        cpu.clock()

    calls = [
        mocker.call.read(expected_status_register_address),
        mocker.call.read(expected_pc_lo_address),
        mocker.call.read(expected_pc_hi_address)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.reg == expected_status_register
    assert cpu.pc == expected_program_counter
    assert cpu.s == expected_stack_pointer

    assert cpu.remaining_cycles == 0

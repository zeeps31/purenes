from unittest import mock

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

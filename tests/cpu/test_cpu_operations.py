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


@pytest.mark.parametrize(
    "accumulator_value, operand_value, negative_flag, zero_flag",
    [
        (0x00, 0x01, 0, 0),
        (0x00, 0x00, 0, 1),
        (0x00, 0x81, 1, 0)
    ],
    ids=[
        "does_not_set_zero_or_negative_flags_when_the_conditions_are_not_met",
        "sets_the_zero_flag_when_the_result_is_zero",
        "sets_the_negative_flag_if_the_result_exceeds_the_signed_8_bit_maximum"
    ]
)
def test_ORA(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        accumulator_value: int,
        operand_value: int,
        negative_flag: int,
        zero_flag: int
):
    """Tests the ORA (Or with Accumulator) operation using opcode 0x01.

    Clocks the CPU and verifies that the following actions are performed during
    the ORA operation.

    1. The accumulator register is correctly ORed with the value or the
       operand.
    2. The negative (N) flag is set under the correct conditions.
    3. The zero (Z) flag is set under the correct conditions.
    """
    cpu.pc = 0x0000
    cpu.a = accumulator_value
    cpu.operand = operand_value

    mock_cpu_bus.read.return_value = 0x01  # Opcode
    mocker.patch.object(cpu, "_retrieve_operand")

    cpu.clock()

    assert cpu.a == accumulator_value | operand_value
    assert cpu.status.flags.negative == negative_flag
    assert cpu.status.flags.zero == zero_flag

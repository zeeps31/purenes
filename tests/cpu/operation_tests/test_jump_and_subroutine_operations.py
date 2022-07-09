from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


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

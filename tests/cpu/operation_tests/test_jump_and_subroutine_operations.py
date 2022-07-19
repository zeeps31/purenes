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


@pytest.mark.parametrize(
    "pc_lo, pc_hi, stack_pointer, expected_lo_address, expected_hi_address, "
    "expected_program_counter, expected_stack_pointer",
    [  # PCL   PCH   S     ELA     EHA     EPC     ES
        (0x00, 0x10, 0xFB, 0x01FB, 0x01FC, 0x1001, 0xFD),
        (0x00, 0x00, 0xFB, 0x01FB, 0x01FC, 0x0001, 0xFD),
    ],
    ids=[
        "executes_successfully_using_opcode_0x60",
        "increments_the_pc_by_one",
    ]
)
def test_RTS(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        pc_lo: int,
        pc_hi: int,
        stack_pointer: int,
        expected_lo_address: int,
        expected_hi_address: int,
        expected_program_counter: int,
        expected_stack_pointer: int):
    """Tests the RTS operation.

    Verifies the following:

    1. The RTS operation is mapped to opcode 0x60.
    2. The program counter is pulled from the stack in order of low to high
       bytes
    3. The program counter is set to the program counter pulled from the stack
       plus one.
    4. The operation completes in 6 clock cycles.
    """
    cpu.pc = 0x0000
    cpu.s = stack_pointer

    opcode: int = 0x60  # Only one opcode for this operation

    mock_cpu_bus.read.side_effect = [
        opcode,
        pc_lo,
        pc_hi,
    ]

    # This operation is always expected to complete in 6 clock cycles.
    for _ in range(0, 6):
        cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # Initial PC read to get opcode
        mocker.call.read(expected_lo_address),
        mocker.call.read(expected_hi_address),
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.s == expected_stack_pointer
    assert cpu.remaining_cycles == 0
    assert cpu.pc == expected_program_counter

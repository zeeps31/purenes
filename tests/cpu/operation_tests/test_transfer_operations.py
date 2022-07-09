from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, effective_address, operation_value, expected_accumulator_value, "
    "expected_x_value, expected_y_value, expected_negative_flag, "
    "expected_zero_flag, expected_cycle_count",
    [
        (0xA0, 0x0000, 0x01, 0x00, 0x00, 0x01, 0, 0, 2),  # LDY
        (0xA1, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 6),  # LDA
        (0xA2, 0x0000, 0x01, 0x00, 0x01, 0x00, 0, 0, 2),  # LDX
        (0xA4, 0x0000, 0x01, 0x00, 0x00, 0x01, 0, 0, 3),  # LDY
        (0xA5, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 3),  # LDA
        (0xA6, 0x0000, 0x01, 0x00, 0x01, 0x00, 0, 0, 3),  # LDX
        (0xA9, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 2),  # LDA
        (0xAC, 0x0000, 0x01, 0x00, 0x00, 0x01, 0, 0, 4),  # LDY
        (0xAD, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 4),  # LDA
        (0xAE, 0x0000, 0x01, 0x00, 0x01, 0x00, 0, 0, 4),  # LDX
        (0xB1, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 5),  # LDA
        (0xB4, 0x0000, 0x01, 0x00, 0x00, 0x01, 0, 0, 4),  # LDY
        (0xB5, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 4),  # LDA
        (0xB6, 0x0000, 0x01, 0x00, 0x01, 0x00, 0, 0, 4),  # LDX
        (0xB9, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 4),  # LDA
        (0xBC, 0x0000, 0x01, 0x00, 0x00, 0x01, 0, 0, 4),  # LDY
        (0xBD, 0x0000, 0x01, 0x01, 0x00, 0x00, 0, 0, 4),  # LDA
        (0xBE, 0x0000, 0x01, 0x00, 0x01, 0x00, 0, 0, 4),  # LDX
        (0xA9, 0x0000, 0x80, 0x80, 0x00, 0x00, 1, 0, 2),  # LDA
        (0xA9, 0x0000, 0x00, 0x00, 0x00, 0x00, 0, 1, 2),  # LDA
        (0xA2, 0x0000, 0x80, 0x00, 0x80, 0x00, 1, 0, 2),  # LDX
        (0xA2, 0x0000, 0x00, 0x00, 0x00, 0x00, 0, 1, 2),  # LDX
        (0xA0, 0x0000, 0x80, 0x00, 0x00, 0x80, 1, 0, 2),  # LDY
        (0xA0, 0x0000, 0x00, 0x00, 0x00, 0x00, 0, 1, 2),  # LDY
    ],
    ids=[
        "LDY_executes_successfully_using_opcode_0xA0",
        "LDA_executes_successfully_using_opcode_0xA1",
        "LDX_executes_successfully_using_opcode_0xA2",
        "LDY_executes_successfully_using_opcode_0xA4",
        "LDA_executes_successfully_using_opcode_0xA5",
        "LDX_executes_successfully_using_opcode_0xA6",
        "LDA_executes_successfully_using_opcode_0xA9",
        "LDY_executes_successfully_using_opcode_0xAC",
        "LDA_executes_successfully_using_opcode_0xAD",
        "LDX_executes_successfully_using_opcode_0xAE",
        "LDA_executes_successfully_using_opcode_0xB1",
        "LDY_executes_successfully_using_opcode_0xB4",
        "LDA_executes_successfully_using_opcode_0xB5",
        "LDX_executes_successfully_using_opcode_0xB6",
        "LDA_executes_successfully_using_opcode_0xB9",
        "LDY_executes_successfully_using_opcode_0xBC",
        "LDA_executes_successfully_using_opcode_0xBD",
        "LDX_executes_successfully_using_opcode_0xBE",
        "LDA_sets_the_negative_flag_correctly",
        "LDA_sets_the_zero_flag_correctly",
        "LDX_sets_the_negative_flag_correctly",
        "LDX_sets_the_zero_flag_correctly",
        "LDY_sets_the_negative_flag_correctly",
        "LDY_sets_the_zero_flag_correctly",
    ]
)
def test_load_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        effective_address: int,
        operation_value,
        expected_accumulator_value: int,
        expected_x_value: int,
        expected_y_value,
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int):
    """Test load instructions.

    Common test for all load instructions.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation loads the operation value stored at the effective address
       into the correct register
    3. The zero and negative flags are set under the correct conditions.
    4. The operation completes in the expected number of clock cycles.
    """
    cpu.effective_address = 0x0000
    cpu.pc = 0x0000
    cpu.operation_value = operation_value
    cpu.x = 0x00
    cpu.y = 0x00
    cpu.a = 0x00
    cpu.status.flags.negative = 0
    cpu.status.flags.zero = 0

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.a == expected_accumulator_value
    assert cpu.x == expected_x_value
    assert cpu.y == expected_y_value
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.remaining_cycles == 0


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
    "opcode, accumulator_value, x_value, y_value, stack_pointer, "
    "expected_accumulator_value, expected_x_value, expected_y_value, "
    "expected_stack_pointer, expected_negative_flag, expected_zero_flag",
    [  # OP    A     X     Y     SP    EA    EX    EY    ESP   N  V
        (0x8A, 0x00, 0x01, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0, 0),  # TXA
        (0x98, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0, 0),  # TYA
        (0x9A, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0, 0),  # TXS
        (0xA8, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0, 0),  # TAY
        (0xAA, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x00, 0x00, 0, 0),  # TAX
        (0xBA, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0, 0),  # TSX
        (0x8A, 0x00, 0x80, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00, 1, 0),  # TXA
        (0x8A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 1),  # TXA
        (0x98, 0x00, 0x00, 0x80, 0x00, 0x80, 0x00, 0x80, 0x00, 1, 0),  # TYA
        (0x98, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 1),  # TYA
        (0xA8, 0x80, 0x00, 0x00, 0x00, 0x80, 0x00, 0x80, 0x00, 1, 0),  # TAY
        (0xA8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 1),  # TAY
        (0xAA, 0x80, 0x00, 0x00, 0x00, 0x80, 0x80, 0x00, 0x00, 1, 0),  # TAX
        (0xAA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 1),  # TAX
        (0xBA, 0x00, 0x00, 0x00, 0x80, 0x00, 0x80, 0x00, 0x80, 1, 0),  # TSX
        (0xBA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0, 1),  # TSX
    ],
    ids=[
        "TXA_transfers_x_to_accumulator",
        "TYA_transfers_y_to_accumulator",
        "TXS_transfers_x_to_stack_pointer",
        "TAY_transfers_accumulator_to_y",
        "TAX_transfers_accumulator_to_x",
        "TSX_transfers_stack_pointer_to_x",
        "TXA_sets_the_zero_flag_correctly",
        "TXA_sets_the_negative_flag_correctly",
        "TYA_sets_the_zero_flag_correctly",
        "TYA_sets_the_negative_flag_correctly",
        "TAY_sets_the_negative_flag_correctly",
        "TAY_sets_the_zero_flag_correctly",
        "TAX_sets_the_negative_flag_correctly",
        "TAX_sets_the_zero_flag_correctly",
        "TSX_sets_the_negative_flag_correctly",
        "TSX_sets_the_zero_flag_correctly",
    ]
)
def test_transfer_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        opcode: int,
        accumulator_value: int,
        x_value: int,
        y_value: int,
        stack_pointer: int,
        expected_accumulator_value: int,
        expected_x_value: int,
        expected_y_value: int,
        expected_stack_pointer: int,
        expected_negative_flag: int,
        expected_zero_flag: int):
    """Test transfer instructions.

    Common test for all transfer instructions.

    Note:
        A test to verify the negative and zero flags are set correctly in the
        TXS operation is intentionally omitted, as this operation does not set
        these flags.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation transfers the value to the appropriate register.
    3. The operation sets the zero and negative flags under the correct
       conditions.
    4. The operation completes in two clock cycles.
    """
    cpu.pc = 0x0000

    cpu.a = accumulator_value
    cpu.x = x_value
    cpu.y = y_value
    cpu.s = stack_pointer

    cpu.status.flags.negative = 0
    cpu.status.flags.zero = 0

    mock_cpu_bus.read.return_value = opcode

    # All transfer instructions use implied addressing and complete in two
    # clock cycles.
    for _ in range(0, 2):
        cpu.clock()

    assert cpu.a == expected_accumulator_value
    assert cpu.x == expected_x_value
    assert cpu.y == expected_y_value
    assert cpu.s == expected_stack_pointer

    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag

    assert cpu.remaining_cycles == 0

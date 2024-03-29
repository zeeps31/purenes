from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, accumulator_value",
    [
        (0x0A, 0xFF),
        (0x2A, 0xFF),
        (0x4A, 0xFF),
        (0x6A, 0xFF),
    ],
    ids=[
        "executes_successfully_using_opcode_0x0A",
        "executes_successfully_using_opcode_0x2A",
        "executes_successfully_using_opcode_0x4A",
        "executes_successfully_using_opcode_0x6A",
    ]
)
def test_accumulator_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int):
    """Tests accumulator addressing mode using opcode 0x0A.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The accumulator is set as the operation value.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.a = accumulator_value

    mock_cpu_bus.read.return_value = opcode

    cpu.clock()

    assert cpu.operation_value == cpu.a


@pytest.mark.parametrize(
    "opcode, operand_lo, operand_hi",
    [
        (0x0D, 0x00, 0x01),
        (0x0E, 0x00, 0x01),
        (0x2C, 0x00, 0x01),
        (0x2D, 0x00, 0x01),
        (0x2E, 0x00, 0x01),
        (0x4D, 0x00, 0x01),
        (0x4E, 0x00, 0x01),
        (0x6D, 0x00, 0x01),
        (0x6E, 0x00, 0x01),
        (0x8C, 0x00, 0x01),
        (0x8D, 0x00, 0x01),
        (0xAC, 0x00, 0x01),
        (0xAD, 0x00, 0x01),
        (0xAE, 0x00, 0x01),
        (0xCC, 0x00, 0x01),
        (0xCD, 0x00, 0x01),
        (0xCE, 0x00, 0x01),
        (0xEC, 0x00, 0x01),
        (0xED, 0x00, 0x01),
        (0xEE, 0x00, 0x01),
    ],
    ids=[
        "executes_successfully_using_opcode_0x0D",
        "executes_successfully_using_opcode_0x0E",
        "executes_successfully_using_opcode_0x2C",
        "executes_successfully_using_opcode_0x2D",
        "executes_successfully_using_opcode_0x2E",
        "executes_successfully_using_opcode_0x4D",
        "executes_successfully_using_opcode_0x4E",
        "executes_successfully_using_opcode_0x6D",
        "executes_successfully_using_opcode_0x6E",
        "executes_successfully_using_opcode_0x8C",
        "executes_successfully_using_opcode_0x8D",
        "executes_successfully_using_opcode_0xAC",
        "executes_successfully_using_opcode_0xAD",
        "executes_successfully_using_opcode_0xAE",
        "executes_successfully_using_opcode_0xCC",
        "executes_successfully_using_opcode_0xCD",
        "executes_successfully_using_opcode_0xCE",
        "executes_successfully_using_opcode_0xEC",
        "executes_successfully_using_opcode_0xED",
        "executes_successfully_using_opcode_0xEE"
    ]
)
def test_absolute_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand_lo: int,
        operand_hi: int):
    """Tests absolute addressing mode.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The low and high bytes of the absolute effective address are read in
       order of low to high.
    3. The operation value is read at the location of the effective address.
    4. The program counter is incremented correctly.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    operation_value: int = 0x01
    effective_address: int = operand_hi << 8 | operand_lo

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand_lo,
        operand_hi,
        operation_value
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get operand low byte
        mocker.call.read(0x0002),  # PC + 2, get operand high byte
        mocker.call.read(effective_address)  # Retrieve operation value
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == operation_value
    assert cpu.pc == 3


@pytest.mark.parametrize(
    "opcode, x_value, y_value, value_address_lo, value_address_hi, "
    "effective_address, cycle_count",
    [
        (0x19, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0x1D, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0x39, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0x3D, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0x3E, 0x02, 0x00, 0x04, 0x00, 0x0006, 7),
        (0x59, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0x5D, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0x5E, 0x02, 0x00, 0x04, 0x00, 0x0006, 7),
        (0x79, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0x7D, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0x7E, 0x02, 0x00, 0x04, 0x00, 0x0006, 7),
        (0x99, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x9D, 0x02, 0x00, 0x04, 0x00, 0x0006, 5),
        (0xB9, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0xBC, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0xBD, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0xBE, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0xD9, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0xDD, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0xDE, 0x02, 0x00, 0x04, 0x00, 0x0006, 7),
        (0xF9, 0x00, 0x02, 0x04, 0x00, 0x0006, 4),
        (0xFD, 0x02, 0x00, 0x04, 0x00, 0x0006, 4),
        (0xFE, 0x02, 0x00, 0x04, 0x00, 0x0006, 7),
        (0x19, 0x00, 0x01, 0xFF, 0x00, 0x0100, 5),
        (0x1D, 0x01, 0x00, 0xFF, 0x00, 0x0100, 5),
    ],
    ids=[
        "executes_successfully_using_opcode_0x19",
        "executes_successfully_using_opcode_0x1D",
        "executes_successfully_using_opcode_0x39",
        "executes_successfully_using_opcode_0x3D",
        "executes_successfully_using_opcode_0x3E",
        "executes_successfully_using_opcode_0x59",
        "executes_successfully_using_opcode_0x5D",
        "executes_successfully_using_opcode_0x5E",
        "executes_successfully_using_opcode_0x7D",
        "executes_successfully_using_opcode_0x7E",
        "executes_successfully_using_opcode_0x79",
        "executes_successfully_using_opcode_0x99",
        "executes_successfully_using_opcode_0x9D",
        "executes_successfully_using_opcode_0xB9",
        "executes_successfully_using_opcode_0xBC",
        "executes_successfully_using_opcode_0xBD",
        "executes_successfully_using_opcode_0xBE",
        "executes_successfully_using_opcode_0xD9",
        "executes_successfully_using_opcode_0xDD",
        "executes_successfully_using_opcode_0xDE",
        "executes_successfully_using_opcode_0xF9",
        "executes_successfully_using_opcode_0xFD",
        "executes_successfully_using_opcode_0xFE",
        "adds_an_extra_cycle_if_a_page_boundary_is_crossed_y",
        "adds_an_extra_cycle_if_a_page_boundary_is_crossed_x"
    ]
)
def test_indexed_absolute_addressing_modes(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        x_value: int,
        y_value: int,
        value_address_lo: int,
        value_address_hi: int,
        effective_address: int,
        cycle_count: int):
    """Tests X and Y indexed absolute addressing mode.

    Note:
        Because this addressing mode has the ability to add an extra
        clock cycle, this test includes cycle_count which is typically tested
        in operation tests.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The low and high bytes of the absolute address are read in order of low
       to high.
    3. The effective address is formed correctly using operand + y or x
    4. An extra cycle is added if a page boundary is crossed.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value
    cpu.y = y_value

    operation_value: int = 0x00

    mock_cpu_bus.read.side_effect = [
        opcode,
        value_address_lo,
        value_address_hi,
        operation_value
    ]

    for _ in range(0, cycle_count):
        cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get operand low byte
        mocker.call.read(0x0002),  # PC + 2, get operand high byte
        mocker.call.read(effective_address)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.effective_address == effective_address
    assert cpu.operation_value == operation_value
    assert cpu.remaining_cycles == 0


@pytest.mark.parametrize(
    "opcode, operand",
    [
        (0x09, 0xFF),
        (0x29, 0xFF),
        (0x49, 0xFF),
        (0x69, 0xFF),
        (0xA0, 0xFF),
        (0xA2, 0xFF),
        (0xA9, 0xFF),
        (0xC0, 0xFF),
        (0xC9, 0xFF),
        (0xE0, 0xFF),
        (0xE9, 0xFF),
    ],
    ids=[
        "executes_successfully_using_opcode_0x09",
        "executes_successfully_using_opcode_0x29",
        "executes_successfully_using_opcode_0x49",
        "executes_successfully_using_opcode_0x69",
        "executes_successfully_using_opcode_0xA0",
        "executes_successfully_using_opcode_0xA2",
        "executes_successfully_using_opcode_0xA9",
        "executes_successfully_using_opcode_0xC0",
        "executes_successfully_using_opcode_0xC9",
        "executes_successfully_using_opcode_0xE0",
        "executes_successfully_using_opcode_0xE9",
    ]
)
def test_immediate_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand: int):
    """Tests immediate addressing mode.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The operand is set as the operation value.
    3. The program counter is incremented
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get operand
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == operand
    assert cpu.pc == 2


@pytest.mark.parametrize(
    "opcode, indirect_address_lo, indirect_address_hi, "
    "expected_indirect_address_lo, expected_indirect_address_hi,"
    "effective_address_lo, effective_address_hi",
    [
        (0x6C, 0x00, 0xFF, 0xFF00, 0xFF01, 0xFF, 0x00),
        (0x6C, 0xFF, 0x00, 0x00FF, 0x0000, 0xFF, 0xFF),
    ],
    ids=[
        "executes_successfully_using_opcode_0x6C",
        "emulates_6502_page_boundary_hardware_bug"
    ]
)
def test_indirect_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        indirect_address_lo: int,
        indirect_address_hi: int,
        expected_indirect_address_lo: int,
        expected_indirect_address_hi: int,
        effective_address_lo: int,
        effective_address_hi: int):
    """Tests indirect addressing mode.

    Verifies the following

    1. The addressing mode is mapped to the correct opcode.
    2. The indirect absolute address is read in order of low to high bytes.
    3. The effective address is retrieved in order of low to high using the
       indirect address and the indirect_address + 1.
    4. The (indirect_address + 1) does not cross page boundaries if the low
       byte is 0xFF. This is a bug in the 6502 processor and recognized by
       this emulator.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    effective_address: int = effective_address_hi << 8 | effective_address_lo

    mock_cpu_bus.read.side_effect = [
        opcode,
        indirect_address_lo,
        indirect_address_hi,
        effective_address_lo,
        effective_address_hi,
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get ind address lo
        mocker.call.read(0x0002),  # PC + 2, get ind address hi
        # Get high and low bytes of effective address from indirect address
        mocker.call.read(expected_indirect_address_lo),
        mocker.call.read(expected_indirect_address_hi)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.effective_address == effective_address


@pytest.mark.parametrize(
    "opcode, operand, x_value, value_address_lo, value_address_hi",
    [
        (0x01, 0x00, 0x02, 0x04, 0x00),
        (0x21, 0x00, 0x02, 0x04, 0x00),
        (0x41, 0x00, 0x02, 0x04, 0x00),
        (0x61, 0x00, 0x02, 0x04, 0x00),
        (0x81, 0x00, 0x02, 0x04, 0x00),
        (0xA1, 0x00, 0x02, 0x04, 0x00),
        (0xC1, 0x00, 0x02, 0x04, 0x00),
        (0xA1, 0x00, 0x02, 0x04, 0x00),
        (0x01, 0xFF, 0x01, 0x04, 0x00),
    ],
    ids=[
        "executes_successfully_using_opcode_0x01",
        "executes_successfully_using_opcode_0x21",
        "executes_successfully_using_opcode_0x41",
        "executes_successfully_using_opcode_0x61",
        "executes_successfully_using_opcode_0x81",
        "executes_successfully_using_opcode_0xA1",
        "executes_successfully_using_opcode_0xC1",
        "executes_successfully_using_opcode_0xE1",
        "wraps_around_when_the_maximum_value_is_reached"
    ]
)
def test_x_indexed_indirect_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand: int,
        x_value: int,
        value_address_lo: int,
        value_address_hi: int):
    """Tests X indexed indirect addressing mode.

    Clocks the CPU and verifies the following actions are performed while
    retrieving the operand:

    1. The addressing mode is mapped to the correct opcode.
    2. The indirect zero-page address is correctly added to the value of x
       and x + 1 to retrieve the high and low bytes of the value address.
    3. The address is wrapped around when necessary.
    4. The low and high bytes of the value address are correctly combined to
       form the effective address.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value

    operation_value: int = 0x00

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand,
        value_address_lo,
        value_address_hi,
        operation_value
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get indirect zero-page address
        mocker.call.read((operand + cpu.x) & 0x00FF),
        mocker.call.read((operand + 1 + cpu.x) & 0x00FF),
        mocker.call.read(value_address_hi << 8 | value_address_lo)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == operation_value


@pytest.mark.parametrize(
    "opcode, operand, y_value, value_address_lo, value_address_hi, "
    "effective_address, cycle_count",
    [
        (0x11, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x31, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x51, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x71, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x91, 0x00, 0x02, 0x04, 0x00, 0x0006, 6),
        (0xB1, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0xD1, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0xF1, 0x00, 0x02, 0x04, 0x00, 0x0006, 5),
        (0x11, 0x00, 0x01, 0xFF, 0x00, 0x0100, 6),

    ],
    ids=[
        "executes_successfully_using_opcode_0x11",
        "executes_successfully_using_opcode_0x31",
        "executes_successfully_using_opcode_0x51",
        "executes_successfully_using_opcode_0x71",
        "executes_successfully_using_opcode_0x91",
        "executes_successfully_using_opcode_0xB1",
        "executes_successfully_using_opcode_0xD1",
        "executes_successfully_using_opcode_0xF1",
        "adds_an_extra_cycle_if_a_page_boundary_is_crossed"
    ]
)
def test_y_indexed_indirect_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand: int,
        y_value: int,
        value_address_lo: int,
        value_address_hi: int,
        effective_address: int,
        cycle_count: int):
    """Tests Y indexed indirect addressing mode.

    Note:
         Because this addressing mode has the ability to add an extra
        clock cycle, this test includes cycle_count which is typically tested
        in operation tests.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The effective address is formed correctly using (opcode, opcode + 1) + y
    3. An extra cycle is added if a page boundary is crossed.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.y = y_value

    operation_value: int = 0x00

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand,
        value_address_lo,
        value_address_hi,
        operation_value
    ]

    for _ in range(0, cycle_count):
        cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get indirect zero-page address
        mocker.call.read(operand & 0x00FF),
        mocker.call.read((operand + 1) & 0x00FF),
        mocker.call.read((value_address_hi << 8 | value_address_lo) + y_value)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.effective_address == effective_address
    assert cpu.operation_value == operation_value
    assert cpu.remaining_cycles == 0


@pytest.mark.parametrize(
    "opcode, operand, operation_value",
    [
        (0x10, 0x00, 0),
        (0x30, 0x00, 0),
        (0x50, 0x00, 0),
        (0x70, 0x00, 0),
        (0x90, 0x00, 0),
        (0xB0, 0x00, 0),
        (0xD0, 0x00, 0),
        (0xF0, 0x00, 0),
        (0x10, 0x80, -128),
        (0x10, 0x7F, 127)
    ],
    ids=[
        "executes_successfully_using_opcode_0x10",
        "executes_successfully_using_opcode_0x30",
        "executes_successfully_using_opcode_0x50",
        "executes_successfully_using_opcode_0x70",
        "executes_successfully_using_opcode_0x90",
        "executes_successfully_using_opcode_0xB0",
        "executes_successfully_using_opcode_0xD0",
        "executes_successfully_using_opcode_0xF0",
        "casts_signed_integers_to_negative_values",
        "casts_signed_integers_to_positive_values"
    ]
)
def test_relative_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand: int,
        operation_value: int,
):
    """Tests relative addressing mode.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The operand is correctly cast to a signed 8-bit value.
    3. The operation value is set to the operand.
    4. The program counter is incremented correctly.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get operand
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == operation_value
    assert cpu.pc == 2


@pytest.mark.parametrize(
    "opcode, operand",
    [
        (0x05, 0xFF),
        (0x06, 0xFF),
        (0x24, 0xFF),
        (0x25, 0xFF),
        (0x26, 0xFF),
        (0x45, 0xFF),
        (0x46, 0xFF),
        (0x65, 0xFF),
        (0x66, 0xFF),
        (0x84, 0xFF),
        (0x85, 0xFF),
        (0xA4, 0xFF),
        (0xA5, 0xFF),
        (0xA6, 0xFF),
        (0xC4, 0xFF),
        (0xC5, 0xFF),
        (0xC6, 0xFF),
        (0xE4, 0xFF),
        (0xE5, 0xFF),
        (0xE6, 0xFF)
    ],
    ids=[
        "executes_successfully_using_opcode_0x05",
        "executes_successfully_using_opcode_0x06",
        "executes_successfully_using_opcode_0x24",
        "executes_successfully_using_opcode_0x25",
        "executes_successfully_using_opcode_0x26",
        "executes_successfully_using_opcode_0x45",
        "executes_successfully_using_opcode_0x46",
        "executes_successfully_using_opcode_0x65",
        "executes_successfully_using_opcode_0x66",
        "executes_successfully_using_opcode_0x84",
        "executes_successfully_using_opcode_0x85",
        "executes_successfully_using_opcode_0xA4",
        "executes_successfully_using_opcode_0xA5",
        "executes_successfully_using_opcode_0xA6",
        "executes_successfully_using_opcode_0xC4",
        "executes_successfully_using_opcode_0xC5",
        "executes_successfully_using_opcode_0xC6",
        "executes_successfully_using_opcode_0xE4",
        "executes_successfully_using_opcode_0xE5",
        "executes_successfully_using_opcode_0xE6",
    ]
)
def test_zero_page_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand: int
):
    """Tests zero-page addressing mode.

    Clocks the CPU and verifies the following actions are performed while
    retrieving the operand:

    1. The address used to retrieve the operation value is $00 + operand
    2. The program counter is incremented correctly.
    """
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    operand: int = operand

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand,  # Zero-page address
        0x01      # Dummy operation value
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # Call to retrieve operand
        mocker.call.read(0x00 | operand),
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.pc == 0x0002


@pytest.mark.parametrize(
    "opcode, x_value, y_value, operand, effective_address",
    [
        (0x15, 0x01, 0x00, 0x00, 0x0001),
        (0x16, 0x01, 0x00, 0x00, 0x0001),
        (0x35, 0x01, 0x00, 0x00, 0x0001),
        (0x36, 0x01, 0x00, 0x00, 0x0001),
        (0x36, 0x01, 0x00, 0x00, 0x0001),
        (0x36, 0x01, 0x00, 0x00, 0x0001),
        (0x56, 0x01, 0x00, 0x00, 0x0001),
        (0x76, 0x01, 0x00, 0x00, 0x0001),
        (0x94, 0x01, 0x00, 0x00, 0x0001),
        (0x95, 0x01, 0x00, 0x00, 0x0001),
        (0x96, 0x00, 0x01, 0x00, 0x0001),
        (0xB4, 0x01, 0x00, 0x00, 0x0001),
        (0xB5, 0x01, 0x00, 0x00, 0x0001),
        (0xB6, 0x00, 0x01, 0x00, 0x0001),
        (0xD5, 0x01, 0x00, 0x00, 0x0001),
        (0xD6, 0x01, 0x00, 0x00, 0x0001),
        (0xF6, 0x01, 0x00, 0x00, 0x0001),
        (0xF6, 0x01, 0x00, 0x00, 0x0001),
        (0x15, 0x02, 0x00, 0xFF, 0x0001),
    ],
    ids=[
        "executes_successfully_using_opcode_0x15",
        "executes_successfully_using_opcode_0x16",
        "executes_successfully_using_opcode_0x35",
        "executes_successfully_using_opcode_0x36",
        "executes_successfully_using_opcode_0x55",
        "executes_successfully_using_opcode_0x56",
        "executes_successfully_using_opcode_0x75",
        "executes_successfully_using_opcode_0x76",
        "executes_successfully_using_opcode_0x94",
        "executes_successfully_using_opcode_0x95",
        "executes_successfully_using_opcode_0x96",
        "executes_successfully_using_opcode_0xB4",
        "executes_successfully_using_opcode_0xB5",
        "executes_successfully_using_opcode_0xB6",
        "executes_successfully_using_opcode_0xD5",
        "executes_successfully_using_opcode_0xD6",
        "executes_successfully_using_opcode_0xF5",
        "executes_successfully_using_opcode_0xF6",
        "wraps_around_when_the_maximum_value_is_reached"
    ]
)
def test_zero_page_indexed_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        x_value: int,
        y_value: int,
        operand: int,
        effective_address: int):
    """Tests zero-page indexed addressing modes (x and y).

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The effective address is set to 0x00 + operand + x or y register
    3. The effective address does not cross pages if the the value of
       operand + index exceeds the unsigned 8-bit maximum.
    """
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value
    cpu.y = y_value
    operand: int = operand

    mock_cpu_bus.read.side_effect = [
        opcode,
        operand,  # Zero-page address
        0x01      # Dummy operation value
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # Call to retrieve operand
        mocker.call.read(effective_address),
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.pc == 0x0002

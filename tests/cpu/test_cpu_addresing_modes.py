from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, accumulator_value",
    [
        (0x0A, 0xFF),
    ],
    ids=[
        "executes_successfully_using_opcode_0x0A",
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
        (0x2D, 0x00, 0x01),
    ],
    ids=[
        "executes_successfully_using_opcode_0x0D",
        "executes_successfully_using_opcode_0x0E",
        "executes_successfully_using_opcode_0x2D"
    ]
)
def test_absolute_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operand_lo: int,
        operand_hi: int):
    """Tests accumulator addressing mode.

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
        (0x19, 0x00, 0x01, 0xFF, 0x00, 0x0100, 5),
        (0x1D, 0x01, 0x00, 0xFF, 0x00, 0x0100, 5),
    ],
    ids=[
        "executes_successfully_using_opcode_0x19",
        "executes_successfully_using_opcode_0x1D",
        "executes_successfully_using_opcode_0x39",
        "executes_successfully_using_opcode_0x3D",
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
    ],
    ids=[
        "executes_successfully_using_opcode_0x09",
        "executes_successfully_using_opcode_0x29",
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
    "opcode, operand, x_value, value_address_lo, value_address_hi",
    [
        (0x01, 0x00, 0x02, 0x04, 0x00),
        (0x21, 0x00, 0x02, 0x04, 0x00),
        (0x01, 0xFF, 0x01, 0x04, 0x00),
    ],
    ids=[
        "executes_successfully_using_opcode_0x01",
        "executes_successfully_using_opcode_0x21",
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
        (0x11, 0x00, 0x01, 0xFF, 0x00, 0x0100, 6),

    ],
    ids=[
        "executes_successfully_using_opcode_0x11",
        "executes_successfully_using_opcode_0x31",
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
        (0x25, 0xFF)
    ],
    ids=[
        "executes_successfully_using_opcode_0x05",
        "executes_successfully_using_opcode_0x06",
        "executes_successfully_using_opcode_0x25",
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
    "opcode, x_value, operand, effective_address",
    [
        (0x15, 0x01, 0x00, 0x0001),
        (0x16, 0x01, 0x00, 0x0001),
        (0x35, 0x01, 0x00, 0x0001),
        (0x15, 0x02, 0xFF, 0x0001),
    ],
    ids=[
        "executes_successfully_using_opcode_0x15",
        "executes_successfully_using_opcode_0x16",
        "executes_successfully_using_opcode_0x35",
        "wraps_around_when_the_maximum_value_is_reached"
    ]
)
def test_zero_page_x_indexed_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        x_value: int,
        operand: int,
        effective_address: int):
    """Tests zero-page x-indexed addressing mode.

    Verifies the following:

    1. The addressing mode is mapped to the correct opcode.
    2. The effective address is set to 0x00 + operand + x
    3. The effective address does not cross pages if the the value of
       operand + x exceeds the unsigned 8-bit maximum.
    """
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value
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

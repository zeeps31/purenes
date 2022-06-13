from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


def test_accumulator_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture):
    """Tests immediate addressing mode using opcode 0x0A.

    Verifies the following:
    1. The accumulator is set as the operation value.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.a = 0xFF

    mock_cpu_bus.read.side_effect = [
        0x0A,  # opcode
    ]

    cpu.clock()

    assert cpu.operation_value == cpu.a


@pytest.mark.parametrize(
    "operand",
    [
        0xFF,
    ],
    ids=[
        "sets_the_operation_value_correctly",
    ]
)
def test_immediate_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        operand: int):
    """Tests immediate addressing mode using opcode 0x09.

    Verifies the following:
    1. The operand is set as the operation value.
    2. The program counter is incremented
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000

    mock_cpu_bus.read.side_effect = [
        0x09,  # opcode
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
    "x_value, indirect_zp_address, value_address_lo, value_address_hi",
    [
        (0x00, 0x02, 0x04, 0x00),
        (0xFF, 0x01, 0x04, 0x00),
    ],
    ids=[
        "retrieves_the_operation_value_correctly",
        "wraps_around_when_the_maximum_value_is_reached"
    ]
)
def test_x_indexed_indirect_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        x_value: int,
        indirect_zp_address: int,
        value_address_lo: int,
        value_address_hi: int):
    """Tests X indexed indirect addressing mode using opcode 0x01.

    Clocks the CPU and verifies the following actions are performed while
    retrieving the operand:

    1. The indirect zero-page address is correctly added to the value of x
       and x + 1 to retrieve the high and low bytes of the value address.
    2. The address is wrapped around when necessary.
    3. The low and high bytes of the value address are correctly combined to
       form the effective address.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value

    operation_value: int = 0x00

    mock_cpu_bus.read.side_effect = [
        0x01,  # opcode
        indirect_zp_address,
        value_address_lo,
        value_address_hi,
        operation_value
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get indirect zero-page address
        mocker.call.read((indirect_zp_address + cpu.x) & 0x00FF),
        mocker.call.read((indirect_zp_address + 1 + cpu.x) & 0x00FF),
        mocker.call.read(value_address_hi << 8 | value_address_lo)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == operation_value


@pytest.mark.parametrize(
    "operand",
    [
        0xFF
    ],
    ids=[
        "retrieves_the_operation_value_correctly",
    ]
)
def test_zero_page_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        operand: int
):
    """Tests zero-page addressing mode using opcode 0x05.

    Clocks the CPU and verifies the following actions are performed while
    retrieving the operand:

    1. The address used to retrieve the operation value is $00 + operand
    2. The program counter is incremented correctly.
    """
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    operand: int = operand

    mock_cpu_bus.read.side_effect = [
        0x05,     # Opcode
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

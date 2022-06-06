from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "x_value, indirect_zp_address, operand_address_lo, operand_address_hi",
    [
        (0x00, 0x02, 0x04, 0x00),
        (0xFF, 0x01, 0x04, 0x00),
    ],
    ids=[
        "retrieves_the_operand_correctly",
        "wraps_around_when_the_maximum_value_is_reached"
    ]
)
def test_x_indexed_indirect_addressing_mode(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        x_value: int,
        indirect_zp_address: int,
        operand_address_lo: int,
        operand_address_hi: int):
    """Tests X indexed indirect addressing mode using opcode 0x01.

    Clocks the CPU and verifies the following actions are performed while
    retrieving the operand:

    1. The indirect zero-page address is correctly added to the value of x
       and x + 1 to retrieve the high and low bytes of the operand address.
    2. The address is wrapped around when necessary.
    3. The low and high bytes of the operand address are correctly ORed when
       retrieving the operand.
    """
    # Patch out the execution of the operation
    mocker.patch.object(cpu, "_execute_operation")

    cpu.pc = 0x0000
    cpu.x = x_value

    operand: int = 0x00

    mock_cpu_bus.read.side_effect = [
        0x01,  # opcode
        indirect_zp_address,
        operand_address_lo,
        operand_address_hi,
        operand
    ]

    cpu.clock()

    calls = [
        mocker.call.read(0x0000),  # First PC read, retrieve opcode
        mocker.call.read(0x0001),  # PC + 1, get indirect zero-page address
        mocker.call.read((indirect_zp_address + cpu.x) & 0x00FF),
        mocker.call.read((indirect_zp_address + 1 + cpu.x) & 0x00FF),
        mocker.call.read(operand_address_hi << 8 | operand_address_lo)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operand == operand

from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, effective_address, operation_value, expected_result, "
    "expected_negative_flag, expected_zero_flag, expected_cycle_count",
    [  # OP    EA      OV    ER    EN EZ EC
        (0xC6, 0x0000, 0x02, 0x01, 0, 0, 5),  # DEC
        (0xCE, 0x0000, 0x02, 0x01, 0, 0, 6),  # DEC
        (0xD6, 0x0000, 0x02, 0x01, 0, 0, 6),  # DEC
        (0xDE, 0x0000, 0x02, 0x01, 0, 0, 7),  # DEC
        (0xE6, 0x0000, 0x00, 0x01, 0, 0, 5),  # INC
        (0xEE, 0x0000, 0x00, 0x01, 0, 0, 6),  # INC
        (0xF6, 0x0000, 0x00, 0x01, 0, 0, 6),  # INC
        (0xFE, 0x0000, 0x00, 0x01, 0, 0, 7),  # INC
        (0xC6, 0x0000, 0x81, 0x80, 1, 0, 5),  # DEC
        (0xC6, 0x0000, 0x01, 0x00, 0, 1, 5),  # DEC
        (0xE6, 0x0000, 0x7F, 0x80, 1, 0, 5),  # DEC
        (0xE6, 0x0000, 0xFF, 0x00, 0, 1, 5),  # DEC
    ],
    ids=[
        "DEC_executes_successfully_using_opcode_0xC6",
        "DEC_executes_successfully_using_opcode_0xCE",
        "DEC_executes_successfully_using_opcode_0xD6",
        "DEC_executes_successfully_using_opcode_0xDE",
        "INC_executes_successfully_using_opcode_0xE6",
        "INC_executes_successfully_using_opcode_0xEE",
        "INC_executes_successfully_using_opcode_0xF6",
        "INC_executes_successfully_using_opcode_0xFE",
        "DEC_sets_the_negative_flag_correctly",
        "DEC_sets_the_zero_flag_correctly",
        "INC_sets_the_negative_flag_correctly",
        "INC_sets_the_zero_flag_correctly",
    ]
)
def test_memory_increment_decrement_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        effective_address: int,
        operation_value: int,
        expected_result: int,
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int):
    """Tests operations that increment and decrement memory values.

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The operation decrements the operation value by one and writes the value
       back to the effective address.
    3. The negative and zero flags are set correctly.
    4. The operation completes in the correct number of clock cycles.
    """
    cpu.pc = 0x0000
    cpu.effective_address = effective_address
    cpu.operation_value = operation_value

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    calls = [
        mocker.call.write(effective_address, expected_result)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.operation_value == expected_result

    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag

    assert cpu.remaining_cycles == 0

from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, accumulator_value, status_value, expected_result, "
    "expected_stack_pointer",
    [  # OP    A     P     ER    ESP
        (0x08, 0x00, 0x00, 0x10, 0xFC),  # PHP
        (0x48, 0xFF, 0x00, 0xFF, 0xFC),  # PHA
    ],
    ids=[
        "PHP_executes_successfully_using_opcode_0x08",
        "PHA_executes_successfully_using_opcode_0x48",
    ]
)
def test_stack_push_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int,
        status_value: int,
        expected_result: int,
        expected_stack_pointer: int
):
    """Tests stack push operations (PHA, PHP).

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The value is pushed to the stack correctly
    3. The stack pointer is decremented by one.
    4. The appropriate flags are set.
    5. The operation completes in 3 clock cycles.
    """
    cpu.pc = 0x0000
    cpu.s = 0xFD
    cpu.a = accumulator_value
    cpu.status.reg = status_value

    mock_cpu_bus.read.return_value = opcode

    for _ in range(0, 3):
        cpu.clock()

    calls = [
        mocker.call.write(0x01FD, expected_result)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.reg == 0x00
    assert cpu.s == expected_stack_pointer
    assert cpu.remaining_cycles == 0


@pytest.mark.parametrize(
    "opcode, accumulator_value, status_value, stack_value, "
    "expected_accumulator_value, expected_status_value, "
    "expected_stack_pointer, expected_negative_flag, expected_zero_flag",
    [  # OP    A     P     SV    EA    EP    ESP  EN  EV
        (0x28, 0x00, 0x00, 0x01, 0x00, 0x01, 0xFD, 0, 0),  # PLP
        (0x68, 0x00, 0x00, 0x01, 0x01, 0x00, 0xFD, 0, 0),  # PLA
        (0x68, 0x00, 0x00, 0x80, 0x80, 0x80, 0xFD, 1, 0),  # PLA
        (0x68, 0x00, 0x00, 0x00, 0x00, 0x02, 0xFD, 0, 1),  # PLA
    ],
    ids=[
        "PLP_executes_successfully_using_opcode_0x28",
        "PLA_executes_successfully_using_opcode_0x68",
        "PLA_sets_the_negative_flag_correctly",
        "PLA_sets_the_zero_flag_correctly",
    ]
)
def test_stack_pull_operations(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        accumulator_value: int,
        status_value: int,
        stack_value: int,
        expected_accumulator_value: int,
        expected_status_value: int,
        expected_stack_pointer: int,
        expected_negative_flag,
        expected_zero_flag
):
    """Tests stack pull operations (PLA, PLP).

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The register under test is set to the value pulled from the stack.
    3. The stack pointer is incremented by one.
    4. The operation completes in 4 clock cycles.
    """
    cpu.pc = 0x0000
    cpu.s = 0xFC
    cpu.a = accumulator_value
    cpu.status.reg = status_value

    mock_cpu_bus.read.side_effect = [
        opcode,
        stack_value
    ]

    for _ in range(0, 4):
        cpu.clock()

    calls = [
        mocker.call.read(0x01FC)
    ]

    mock_cpu_bus.assert_has_calls(calls)

    assert cpu.status.reg == expected_status_value
    assert cpu.s == expected_stack_pointer
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag
    assert cpu.remaining_cycles == 0

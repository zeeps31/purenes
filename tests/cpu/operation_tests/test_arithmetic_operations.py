from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, operation_value, accumulator_value, carry_flag, expected_result, "
    "expected_carry_flag, expected_overflow_flag, expected_negative_flag, "
    "expected_zero_flag, expected_cycle_count",
    [  # OP    OV    A     C  ER    EC EV EN EZ EC
        (0x61, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 6),
        (0x65, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 3),
        (0x69, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 2),
        (0x6D, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),
        (0x71, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 5),
        (0x75, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),
        (0x79, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),
        (0x7D, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),
        (0x61, 0x01, 0x7F, 0, 0x80, 0, 1, 1, 0, 6),
        (0x61, 0x00, 0x00, 0, 0x00, 0, 0, 0, 1, 6),
        (0x61, 0xFF, 0xFF, 0, 0xFE, 1, 0, 1, 0, 6),
        (0x61, 0x01, 0xFF, 0, 0x00, 1, 0, 0, 1, 6)
    ],
    ids=[
        "executes_successfully_using_opcode_0x61",
        "executes_successfully_using_opcode_0x65",
        "executes_successfully_using_opcode_0x69",
        "executes_successfully_using_opcode_0x6D",
        "executes_successfully_using_opcode_0x71",
        "executes_successfully_using_opcode_0x75",
        "executes_successfully_using_opcode_0x79",
        "executes_successfully_using_opcode_0x7D",
        "sets_the_overflow_flag_correctly",
        "sets_the_zero_flag_correctly",
        "sets_the_carry_flag_correctly",
        "sets_the_zero_flag_when_results_exceed_maximum",
    ]
)
def test_ADC(
        cpu: purenes.cpu.CPU,
        mock_cpu_bus: mock.Mock,
        mocker: pytest_mock.MockFixture,
        opcode: int,
        operation_value: int,
        accumulator_value: int,
        carry_flag: int,
        expected_result: int,
        expected_carry_flag: int,
        expected_overflow_flag: int,
        expected_negative_flag: int,
        expected_zero_flag: int,
        expected_cycle_count: int):
    """Tests ADC operation

    Verifies the following:

    1. The operation is mapped to the correct opcode.
    2. The accumulator, operation_value and carry are added together and
       written back to the accumulator.
    3. The carry, overflow, negative and zero flags are set under the correct
       conditions.
    4. The operation completes in the correct number of clock cycles.
    """
    cpu.pc = 0x0000
    cpu.operation_value = operation_value
    cpu.a = accumulator_value
    cpu.status.flags.carry = carry_flag

    mock_cpu_bus.read.return_value = opcode
    mocker.patch.object(cpu, "_retrieve_operation_value")

    for _ in range(0, expected_cycle_count):
        cpu.clock()

    assert cpu.a == expected_result

    assert cpu.status.flags.carry == expected_carry_flag
    assert cpu.status.flags.overflow == expected_overflow_flag
    assert cpu.status.flags.negative == expected_negative_flag
    assert cpu.status.flags.zero == expected_zero_flag

    assert cpu.remaining_cycles == 0

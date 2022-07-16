from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.mark.parametrize(
    "opcode, operation_value, accumulator_value, carry_flag, expected_result, "
    "expected_carry_flag, expected_overflow_flag, expected_negative_flag, "
    "expected_zero_flag, expected_cycle_count",
    [  # OP    OV    A     C  ER    EC EV EN EZ EC
        (0x61, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 6),  # ADC
        (0x65, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 3),  # ADC
        (0x69, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 2),  # ADC
        (0x6D, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),  # ADC
        (0x71, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 5),  # ADC
        (0x75, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),  # ADC
        (0x79, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),  # ADC
        (0x7D, 0x02, 0x01, 0, 0x03, 0, 0, 0, 0, 4),  # ADC
        (0xE1, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 6),  # SBC
        (0xE5, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 3),  # SBC
        (0xE9, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 2),  # SBC
        (0xED, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 4),  # SBC
        (0xF1, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 5),  # SBC
        (0xF5, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 4),  # SBC
        (0xF9, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 4),  # SBC
        (0xFD, 0x01, 0x02, 1, 0x01, 1, 0, 0, 0, 4),  # SBC
        (0x61, 0x01, 0x7F, 0, 0x80, 0, 1, 1, 0, 6),  # ADC
        (0x61, 0x00, 0x00, 0, 0x00, 0, 0, 0, 1, 6),  # ADC
        (0x61, 0xFF, 0xFF, 0, 0xFE, 1, 0, 1, 0, 6),  # ADC
        (0x61, 0x01, 0xFF, 0, 0x00, 1, 0, 0, 1, 6),  # ADC
        (0xE1, 0xB0, 0x50, 1, 0xA0, 0, 1, 1, 0, 6),  # SBC
        (0xE9, 0x01, 0x01, 1, 0x00, 1, 0, 0, 1, 6),  # SBC
        (0xE9, 0x01, 0x00, 1, 0xFF, 0, 0, 1, 0, 6),  # SBC
    ],
    ids=[
        "ADC_executes_successfully_using_opcode_0x61",
        "ADC_executes_successfully_using_opcode_0x65",
        "ADC_executes_successfully_using_opcode_0x69",
        "ADC_executes_successfully_using_opcode_0x6D",
        "ADC_executes_successfully_using_opcode_0x71",
        "ADC_executes_successfully_using_opcode_0x75",
        "ADC_executes_successfully_using_opcode_0x79",
        "ADC_executes_successfully_using_opcode_0x7D",
        "SBC_executes_successfully_using_opcode_0xE1",
        "SBC_executes_successfully_using_opcode_0xE5",
        "SBC_executes_successfully_using_opcode_0xE9",
        "SBC_executes_successfully_using_opcode_0xED",
        "SBC_executes_successfully_using_opcode_0xF1",
        "SBC_executes_successfully_using_opcode_0xF5",
        "SBC_executes_successfully_using_opcode_0xF9",
        "SBC_executes_successfully_using_opcode_0xFD",
        "ADC_sets_the_overflow_flag_correctly",
        "ADC_sets_the_zero_flag_correctly",
        "ADC_sets_the_carry_flag_correctly",
        "ADC_sets_the_zero_flag_when_result_exceeds_maximum",
        "SBC_sets_the_overflow_flag_correctly",
        "SBC_sets_the_zero_flag_correctly",
        "SBC_sets_the_borrow_flag_correctly",
    ]
)
def test_arithmetic_operations(
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

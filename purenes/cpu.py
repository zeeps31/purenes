# Python 3.7 and 3.8 support
try:
    from typing import Final  # pragma: no cover
    from typing import TypedDict  # pragma: no cover
except ImportError:  # pragma: no cover
    from typing_extensions import Final  # pragma: no cover
    from typing_extensions import TypedDict  # pragma: no cover

import ctypes
from typing import Callable
from typing import Dict
from typing import List
from typing import Tuple


class CPUStatus(ctypes.Union):
    """A class to represent the CPU status register (P).

    https://www.nesdev.org/wiki/Status_flags

    The values detailed below can be accessed using the
    :attr:`~purenes.cpu._Status.flags` attribute of this class.

    * carry             (C) - Carry flag.
    * zero              (Z) - Zero flag.
    * interrupt_disable (I) - Interrupt disable flag.
    * decimal           (D) - Decimal flag. On the NES, has no effect.
    * brk               (B) - Break flag.
    * na                (s) - Unused
    * overflow          (V) - Overflow flag.
    * negative          (N) - Negative flag.
    """
    _fields_ = [
        ("flags", type(
            "_CPUStatus",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("carry",             ctypes.c_uint8, 1),
                ("zero",              ctypes.c_uint8, 1),
                ("interrupt_disable", ctypes.c_uint8, 1),
                ("decimal",           ctypes.c_uint8, 1),
                ("brk",               ctypes.c_uint8, 1),
                ("na",                ctypes.c_uint8, 1),
                ("overflow",          ctypes.c_uint8, 1),
                ("negative",          ctypes.c_uint8, 1),
            ]}
        )),
        ("reg", ctypes.c_uint8)]


class CPUBus(object):
    """
    A class to represent the NES CPU bus.

    The CPU bus is responsible for handling the logic of delegating reads and
    writes to the correct resource connected to the CPU based on the CPU
    memory map.

    https://www.nesdev.org/wiki/CPU_memory_map.

    +----------------+------+-----------------------------------------------+
    | Address range  | Size | Device                                        |
    +================+======+===============================================+
    | $0000-$07FF    |$0800 | 2KB internal RAM                              |
    +----------------+------+-----------------------------------------------+
    | $0800-$0FFF    |$0800 | Mirrors of $0000-$07FF                        |
    | $1000-$17FF    |$0800 |                                               |
    | $1800-$1FFF    |$0800 |                                               |
    +----------------+------+-----------------------------------------------+
    | $2000-$2007    |$0008 | NES PPU registers                             |
    | $2008-$3FFF    |$1FF8 | Mirrors of $2000-2007 (repeats every 8 bytes) |
    +----------------+------+-----------------------------------------------+
    | $4000-$4017    |$0018 | NES APU and I/O registers                     |
    +----------------+------+-----------------------------------------------+
    | $4018-$401F    |$0008 | APU and I/O functionality.                    |
    +----------------+------+-----------------------------------------------+
    | $4020-$FFFF    |$BFE0 | Cartridge space: PRG ROM, PRG RAM, and mapper |
    +----------------+------+-----------------------------------------------+
    """
    # TODO: https://github.com/zeeps31/purenes/issues/6
    _INVALID_ADDRESS_EXCEPTION: Final = ("Invalid address provided: "
                                         "{address}. Address should be "
                                         "between 0x0000 - 0xFFFF")

    _RAM_ADDRESS_MASK: Final = 0x1FF

    _ram: List[int]

    def __init__(self):
        """Connects devices to the CPU and initializes the devices based on
        reset and startup behaviors.
        """
        # Internal memory ($0000-$07FF) has unreliable startup state.
        # Some machines may have consistent RAM contents at power-on,
        # but others do not. Here, the ram is initialized to a 2KB
        # array of 0x00 values.
        self._ram = [0x00] * 0x0800

    def read(self, address: int) -> int:
        """Reads a value from the appropriate resource connected to the CPU.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value from the specified address location.
        """
        if 0x0000 <= address <= 0x1FFF:
            return self._ram[address & self._RAM_ADDRESS_MASK]

        else:
            raise Exception(
                self._INVALID_ADDRESS_EXCEPTION.format(
                    address=hex(address)
                )
            )

    def write(self, address: int, data: int) -> None:
        """Writes a value from the appropriate resource connected to the CPU.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None
        """
        if 0x0000 <= address <= 0x1FFF:
            self._ram[address & self._RAM_ADDRESS_MASK] = data

        else:
            raise Exception(
                self._INVALID_ADDRESS_EXCEPTION.format(
                    address=hex(address)
                )
            )


class CPU(object):
    """A non-cycle-accurate implementation of the MOS6502 processor.

    Each time the CPU is clocked, the addressing mode and operation are
    performed on the first clock cycle. A counter is used to track the
    remaining clock cycles for the operation. For each subsequent clock no
    action is performed until the counter reaches 0.

    Note:
        The attributes listed below are exposed publicly to allow testing and
        debugging processes to explicitly set and interrogate these values.
        These values should not be accessed directly under normal
        circumstances.

        Internal Registers, Stack Pointer and Program Counter:
            :attr:`~purenes.cpu.CPU.a`
            :attr:`~purenes.cpu.CPU.x`
            :attr:`~purenes.cpu.CPU.y`
            :attr:`~purenes.cpu.CPU.pc`
            :attr:`~purenes.cpu.CPU.s`

        Active Opcode, Operation Value, Effective Address and Remaining Cycles:
            :attr:`~purenes.cpu.CPU.opcode`
            :attr:`~purenes.cpu.CPU.operation_value`
            :attr:`~purenes.cpu.CPU.effective_address`
            :attr:`~purenes.cpu.CPU.remaining_cycles`
    """
    _RES: Final[int] = 0xFFFC  # Reset vector low bytes
    _IRQ: Final[int] = 0xFFFE  # Interrupt vector low bytes

    a:  int                          #: Accumulator register.
    x:  int                          #: X index register.
    y:  int                          #: Y index register.
    pc: int                          #: The 16-bit program counter for the CPU.
    s:  int                          #: Stack pointer.
    status: CPUStatus = CPUStatus()  #: Status register (P).

    opcode:  int  #: The opcode that the CPU is currently executing.
    operation_value: int  #: The value retrieved using the addressing mode.

    #: The "effective address" is the address that contains the value needed
    #: by the operation. The effective address is either formed from the
    #: operand, or is the operand itself (E.g. absolute addressing).
    effective_address: int

    # The internal bus for the CPU
    _cpu_bus: CPUBus

    #: Tracks the total number of cycles that have been performed.
    remaining_cycles: int = 0

    _operations:      Dict[int, Tuple[Callable, Callable, int]]
    _operation:       Callable  # The current operation
    _addressing_mode: Callable  # The addressing mode for the current operation

    def __init__(self, cpu_bus: CPUBus):
        """Connect the :class:`~purenes.cpu.CPUBus` to the CPU.

        Note:
            None of the internal registers are initialized at this point. This
            does not happen until :func:`~purenes.cpu.CPU.reset` is called.

        Args:
            cpu_bus (CPUBus): An instance of a :class:`~purenes.cpu.CPUBus`
        """
        self._cpu_bus = cpu_bus
        self._map_operations()

    def clock(self) -> None:
        """Perform one CPU "tick". The clock method is the main entry-point
        into the CPU.

        Each time the CPU is clocked and the remaining cycle counter is 0, the
        following events occur:

        1. The CPU reads from :class:`~purenes.cpu.CPUBus` at the address
           stored in the program counter.
        2. The program counter is incremented by one.
        3. The operation retrieved from the address at the program counter is
           executed.

        If there are still remaining cycles for the operation, the remaining
        cycle counter is decremented and no action is performed.

        Returns:
            None
        """
        if self.remaining_cycles == 0:
            self.opcode = self._read(self.pc)
            self.pc += 1

            self._load_operation()

            self._retrieve_operation_value()
            self._execute_operation()

        self.remaining_cycles -= 1

    def reset(self) -> None:
        """Perform power-up and reset procedures for the CPU.

        https://www.masswerk.at/6502/6502_instruction_set.html

        As the reset the processor performs a start sequence of 7 cycles, at
        the end of which the program counter (PC) is read from the address
        provided in the 16-bit reset vector at $FFFC (LB-HB). Then, at the
        eighth cycle, the processor transfers control by performing a JMP to
        the provided address. Any other initializations are left to the thus
        executed program. (Notably, instructions exist for the initialization
        and loading of all registers, but for the program counter, which is
        provided by the reset vector at $FFFC.)

        Returns:
            None
        """
        # Perform reset actions.
        self.a = 0x00
        self.x = 0x00
        self.y = 0x00
        self.s = 0xFD
        self.status.reg |= 0x04

        pc_lo: int = self._read(self._RES)
        pc_hi: int = self._read(self._RES + 1)

        self.pc = pc_hi << 8 | pc_lo

        # As the reset line goes high the processor performs a start sequence
        # of 7 cycles
        self.remaining_cycles += 7

    def _read(self, address: int) -> int:
        return self._cpu_bus.read(address)

    def _write(self, address: int, data: int) -> None:
        self._cpu_bus.write(address, data)

    def _load_operation(self) -> None:
        operation: Tuple[Callable, Callable, int] = self._operations[
            self.opcode]

        self._addressing_mode = operation[0]
        self._operation = operation[1]
        self.remaining_cycles += operation[2]

    def _retrieve_operation_value(self):
        # Execute the addressing mode required by the current operation to
        # retrieve the operand.
        self._addressing_mode()

    def _execute_operation(self):
        # Perform the current operation.
        self._operation()

    # Private utility methods

    def _push_to_stack(self, data: int) -> None:
        # Push a value to the stack. The stack is implemented at addresses
        # $0100 - $01FF and is a LIFO stack. A push to the stack decrements the
        # stack pointer by 1.
        self._write(0x0100 | self.s, data)
        self.s -= 1

    def _pull_from_stack(self) -> int:
        # Pull a value from the stack. The stack is implemented at addresses
        # $0100 - $01FF and is a LIFO stack. A pull from the stack increments
        # the stack pointer by 1.
        data: int = self._read(0x0100 | self.s)
        self.s += 1
        return data

    def _execute_branch_operation(self):
        # Common function to execute branching instructions.
        self.remaining_cycles += 1
        self.effective_address = self.pc + self.operation_value

        # Check if page boundary was crossed. Add an extra cycle if True.
        if (self.effective_address & 0xFF00) != (self.pc & 0xFF00):
            self.remaining_cycles += 1

        self.pc = self.effective_address

    def _read_absolute_address(self):
        # Common function used by addressing modes to read a 16-bit absolute
        # address. Sets the effective address to absolute address.
        lo: int = self._read(self.pc)
        self.pc += 1

        hi: int = self._read(self.pc)
        self.pc += 1

        self.effective_address = hi << 8 | lo

    def _increment_address_with_carry(self, address: int, increment: int):
        # Common function to increment a 16-bit address with carry.
        self.effective_address = address + increment

        # Check if page cross occurred. If so, add an extra cycle
        if (self.effective_address & 0xFF00) != (address & 0xFF00):
            self.remaining_cycles += 1

    def _execute_increment_operation(self, value: int) -> int:
        # Used by increment operations to increment a value, wrap-around upon
        # integer overflow, set negative and zero flags, and return the value.
        value = (value + 1) & 0xFF

        self._set_negative_flag(value)
        self._set_zero_flag(value)

        return value

    def _execute_decrement_operation(self, value: int) -> int:
        # Used by decrement operations to increment a value, wrap-around upon
        # integer overflow, set negative and zero flags, and return the value.
        value = (value - 1) & 0xFF

        self._set_negative_flag(value)
        self._set_zero_flag(value)

        return value

    def _write_operation_result(self, value: int):
        # Common function to write an operation result back to a location.

        # If this is accumulator addressing mode write the value back to the
        # accumulator, otherwise, write to the effective address.
        if self._addressing_mode == self._acc:
            self.a = value
        else:
            self._write(self.effective_address, value)

    def _set_negative_flag(self, value: int):
        # Set the negative flag if the two's complement MSB is 1.
        self.status.flags.negative = (value & 0x80) != 0x00

    def _set_zero_flag(self, value: int):
        # Sets the zero flag if the result of an operation is 0.
        self.status.flags.zero = value == 0x00

    def _set_carry_flag(self, value: int):
        # Sets the carry flag if the MSB of the current value is 1.
        self.status.flags.carry = (value & 0x80) != 0

    def _set_overflow_flag(self, x: int, y: int, result: int):
        # Sets the overflow flag based on the condition that the signed bits
        # of the input values (x and y) are the same and the signed bits of
        # the input values differ from that of the result.
        input_signs_are_the_same: bool = not ((x ^ y) & 0x80)
        input_and_result_signs_differ: bool = ((x ^ result) & 0x80) != 0

        self.status.flags.overflow = (
            input_signs_are_the_same
            and
            input_and_result_signs_differ
        )

    # Addressing Modes

    def _acc(self):
        # Accumulator addressing mode. The operand and operation value are the
        # value currently stored in the accumulator.
        self.operation_value = self.a

    def _abs(self):
        # Absolute addressing mode. Operand is address $HHLL.
        self._read_absolute_address()
        self.operation_value = self._read(self.effective_address)

    def _abx(self):
        # Absolute X-indexed addressing mode. Effective address is operand
        # incremented by X with carry.
        self._read_absolute_address()
        operand: int = self.effective_address

        self._increment_address_with_carry(operand, self.x)

        self.operation_value = self._read(self.effective_address)

    def _aby(self):
        # Absolute Y-indexed addressing mode. Effective address is operand
        # incremented by Y with carry.
        self._read_absolute_address()
        operand: int = self.effective_address

        self._increment_address_with_carry(operand, self.y)

        self.operation_value = self._read(self.effective_address)

    def _imm(self):
        # Immediate addressing mode. Operand and operation value is byte BB
        # (#$BB).
        self.operation_value = self._read(self.pc)
        self.pc += 1

    def _imp(self):
        # Implied addressing mode. In this mode the operand is implied by the
        # operation.
        return

    def _ind(self):
        # Indirect addressing mode. Operand is address; effective address is
        # contents of word at address.
        self._read_absolute_address()

        # Denote this is a "pointer" to the effective address for readability.
        address: int = self.effective_address

        lo: int = self._read(address)
        # Emulate hardware bug in 6502 processor that wraps the low byte of the
        # address around upon a page boundary cross.
        if ((address + 1) & 0xFF00) != address & 0xFF00:
            hi: int = self._read(address & 0xFF00)
        else:
            hi: int = self._read(address + 1)

        self.effective_address = hi << 8 | lo

    def _izx(self):
        # X-indexed indirect addressing mode.

        # The operand is a zero-page address. This value is added with the x
        # register to form the effective address. This addressing mode wraps
        # around for values larger than $FF.
        operand: int = self._read(self.pc)
        self.pc += 1

        lo: int = self._read((operand + self.x) & 0x00FF)
        hi: int = self._read((operand + self.x + 1) & 0x00FF)

        self.effective_address = hi << 8 | lo
        self.operation_value = self._read(self.effective_address)

    def _izy(self):
        # Y-indexed indirect addressing mode.

        # The operand is a zero-page address. The effective address is formed
        # as follows: (operand, operand + 1) + y.
        operand: int = self._read(self.pc)
        self.pc += 1

        lo: int = self._read((operand & 0x00FF))
        hi: int = self._read((operand + 1) & 0x00FF)

        self._increment_address_with_carry((hi << 8 | lo), self.y)

        self.operation_value = self._read(self.effective_address)

    def _rel(self):
        # Relative addressing mode. Only used with branching instructions.

        # The operand in this addressing mode is a signed 8-bit value
        # -128 ... +127 and can increment or decrement the program counter in
        # this range.
        operand: int = self._read(self.pc)
        self.pc += 1

        # Cast operand to a signed offset.
        self.operation_value = ctypes.c_int8(operand).value

    def _zpg(self):
        # Zero page addressing mode. Address = $00LL.
        operand: int = self._read(self.pc)
        self.effective_address = operand
        self.operation_value = self._read(self.effective_address)
        self.pc += 1

    def _zpx(self):
        # Zero page X indexed addressing mode. Address is operand + X without
        # carry.
        operand: int = self._read(self.pc)
        self.pc += 1

        self.effective_address = (operand + self.x) & 0x00FF
        self.operation_value = self._read(self.effective_address)

    def _zpy(self):
        # Zero page Y indexed addressing mode. Address is operand + Y without
        # carry.
        operand: int = self._read(self.pc)
        self.pc += 1

        self.effective_address = (operand + self.y) & 0x00FF
        self.operation_value = self._read(self.effective_address)

    # Operations

    # Transfer Instructions

    def _LDA(self):
        # Load Accumulator with Memory
        self.a = self.operation_value

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    def _LDX(self):
        # Load Index X with Memory
        self.x = self.operation_value

        self._set_negative_flag(self.x)
        self._set_zero_flag(self.x)

    def _LDY(self):
        # Load Index Y with Memory
        self.y = self.operation_value

        self._set_negative_flag(self.y)
        self._set_zero_flag(self.y)

    def _STA(self):
        # Store Accumulator in Memory
        self._write_operation_result(self.a)

    def _STX(self):
        # Store Index X in Memory
        self._write(self.effective_address, self.x)

    def _STY(self):
        # Store Index Y in Memory
        self._write_operation_result(self.y)

    def _TAX(self):
        # Transfer Accumulator to Index X
        self.x = self.a

        self._set_negative_flag(self.x)
        self._set_zero_flag(self.x)

    def _TAY(self):
        # Transfer Accumulator to Index Y
        self.y = self.a

        self._set_negative_flag(self.y)
        self._set_zero_flag(self.y)

    def _TSX(self):
        # Transfer Stack Pointer to Index X
        self.x = self.s

        self._set_negative_flag(self.x)
        self._set_zero_flag(self.x)

    def _TXA(self):
        # Transfer Index X to Accumulator
        self.a = self.x

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    def _TXS(self):
        # Transfer Index X to Stack Register
        self.s = self.x

    def _TYA(self):
        # Transfer Index Y to Accumulator
        self.a = self.y

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    # Stack Instructions

    def _PHA(self):
        # Push Accumulator on Stack
        self._push_to_stack(self.a)

    def _PHP(self):
        # Push Processor Status on Stack.
        self.status.flags.brk = 1
        self._push_to_stack(self.status.reg)
        self.status.flags.brk = 0

    def _PLA(self):
        # Pull Accumulator from Stack
        self.a = self._pull_from_stack()

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    def _PLP(self):
        # Pull Processor Status from Stack.
        self.status.reg = self._pull_from_stack()

    # Decrements and Increments

    def _DEC(self):
        # Decrement Memory by One
        self.operation_value = self._execute_decrement_operation(
            self.operation_value)

        self._write_operation_result(self.operation_value)

    def _DEX(self):
        # Decrement Index X by One
        self.x = self._execute_decrement_operation(self.x)

    def _DEY(self):
        # Decrement Index Y by One
        self.y = self._execute_decrement_operation(self.y)

    def _INC(self):
        # Increment Memory by One
        self.operation_value = self._execute_increment_operation(
            self.operation_value)

        self._write_operation_result(self.operation_value)

    def _INX(self):
        # Increment Index X by One
        self.x = self._execute_increment_operation(self.x)

    def _INY(self):
        # Increment Index Y by One
        self.y = self._execute_increment_operation(self.y)

    # Arithmetic Operations

    def _ADC(self):
        # Add Memory to Accumulator with Carry
        result: int = self.a + self.operation_value + self.status.flags.carry

        # Set the carry flag if the result has exceeded the 8-bit maximum
        self.status.flags.carry = result > 0xFF
        self._set_overflow_flag(self.a, self.operation_value, result)

        # "Cast" result to 8-bit value, store in accumulator
        self.a = result & 0xFF

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    def _SBC(self):
        # Subtract Memory from Accumulator with Borrow.
        #
        # Set the operation_value to the ones complement and perform an ADC.
        # The twos complement is obtained from the addition of the carry
        # (borrow) flag, which is required to be set before this operation is
        # performed.
        self.operation_value = self.operation_value ^ 0xFF
        self._ADC()

    # Logical Operations

    def _AND(self):
        # And with the accumulator
        self.a &= self.operation_value

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    def _ORA(self):
        # OR with the accumulator.
        self.a |= self.operation_value

        self._set_negative_flag(self.a)
        self._set_zero_flag(self.a)

    # Shift and Rotate Instructions

    def _ASL(self):
        # Arithmetic shift left. Shifts in a zero bit on the right.

        # The 7th bit of the operation value is preserved in the carry flag.
        self._set_carry_flag(self.operation_value)

        self.operation_value = (self.operation_value << 1) & 0x00FF
        self._write_operation_result(self.operation_value)

        self._set_negative_flag(self.operation_value)
        self._set_zero_flag(self.operation_value)

    def _ROL(self):
        # Rotate One Bit Left (Memory or Accumulator). The Carry is shifted
        # into bit 0 and the original bit 7 is shifted into the Carry.
        carry: int = self.status.flags.carry
        self._set_carry_flag(self.operation_value)

        self.operation_value = (self.operation_value << 1 | carry) & 0x00FF
        self._write_operation_result(self.operation_value)

        self._set_negative_flag(self.operation_value)
        self._set_zero_flag(self.operation_value)

    # Flag Instructions

    def _CLC(self):
        # Clear carry flag.
        self.status.flags.carry = 0

    def _CLD(self):
        # Clear decimal mode
        self.status.flags.decimal = 0

    def _CLI(self):
        # Clear interrupt disable
        self.status.flags.interrupt_disable = 0

    def _CLV(self):
        # Clear overflow flag
        self.status.flags.overflow = 0

    def _SEC(self):
        # Set carry flag
        self.status.flags.carry = 1

    def _SED(self):
        # Set decimal flag
        self.status.flags.decimal = 1

    def _SEI(self):
        # Set interrupt disable
        self.status.flags.interrupt_disable = 1

    # Conditional Branch Instructions

    def _BCC(self):
        # Branch on carry clear (C = 0)
        if self.status.flags.carry == 0:
            self._execute_branch_operation()

    def _BCS(self):
        # Branch on carry set (C = 1)
        if self.status.flags.carry == 1:
            self._execute_branch_operation()

    def _BNE(self):
        # Branch on not equal (Z = 0)
        if self.status.flags.zero == 0:
            self._execute_branch_operation()

    def _BEQ(self):
        # Branch on equal (Z = 1)
        if self.status.flags.zero == 1:
            self._execute_branch_operation()

    def _BPL(self):
        # Branch on result plus (N = 0).
        if self.status.flags.negative == 0:
            self._execute_branch_operation()

    def _BMI(self):
        # Branch on result minus (N = 1).
        if self.status.flags.negative == 1:
            self._execute_branch_operation()

    def _BVC(self):
        # Branch on overflow clear (V = 0)
        if self.status.flags.overflow == 0:
            self._execute_branch_operation()

    def _BVS(self):
        # Branch on overflow set (V = 1)
        if self.status.flags.overflow == 1:
            self._execute_branch_operation()

    # Jumps & Subroutines

    def _JMP(self):
        # Jump to a new location.
        self.pc = self.effective_address

    def _JSR(self):
        # Jump to New Location Saving Return Address.

        # On the hardware implementation the PC is pushed before the second
        # address byte is read. The PC needs to be decremented by 1 to emulate
        # this behavior.
        self.pc -= 1

        self._push_to_stack(self.pc >> 8)
        self._push_to_stack(self.pc & 0x00FF)

        # Program counter is set to the absolute effective address
        self.pc = self.effective_address

    # Interrupts

    def _BRK(self):
        # BRK initiates a software interrupt similar to a hardware interrupt
        # (IRQ).

        # The return address pushed to the stack is PC+2, providing an extra
        # byte of spacing for a break mark (reason for the break).
        self.pc += 1

        self.status.flags.interrupt_disable = 1
        self.status.flags.brk = 1

        self._push_to_stack(self.pc >> 8)
        self._push_to_stack(self.pc & 0x00FF)

        self._push_to_stack(self.status.reg)

        self.pc = self._read(self._IRQ) | self._read(self._IRQ + 1) << 8

    # Other

    def _BIT(self):
        # Test Bits in Memory with Accumulator
        self.status.flags.negative = self.operation_value >> 7
        self.status.flags.overflow = (self.operation_value >> 6) & 0x01
        self.status.flags.zero = (self.operation_value & self.a) == 0

    def _map_operations(self) -> None:
        # Map operations and addressing modes to opcodes.
        op = self
        self._operations = {
            0x00: (op._imp, op._BRK, 7), 0x01: (op._izx, op._ORA, 6),
            0x05: (op._zpg, op._ORA, 3), 0x06: (op._zpg, op._ASL, 5),
            0x08: (op._imp, op._PHP, 3), 0x09: (op._imm, op._ORA, 2),
            0x0A: (op._acc, op._ASL, 2), 0x0D: (op._abs, op._ORA, 4),
            0x0E: (op._abs, op._ASL, 6), 0x10: (op._rel, op._BPL, 2),
            0x11: (op._izy, op._ORA, 5), 0x15: (op._zpx, op._ORA, 4),
            0x16: (op._zpx, op._ASL, 6), 0x18: (op._imp, op._CLC, 2),
            0x19: (op._aby, op._ORA, 4), 0x1D: (op._abx, op._ORA, 4),
            0x1E: (op._abx, op._ASL, 7), 0x20: (op._abs, op._JSR, 6),
            0x21: (op._izx, op._AND, 6), 0x24: (op._zpg, op._BIT, 3),
            0x25: (op._zpg, op._AND, 3), 0x26: (op._zpg, op._ROL, 5),
            0x28: (op._imp, op._PLP, 4), 0x29: (op._imm, op._AND, 2),
            0x2A: (op._acc, op._ROL, 2), 0x2C: (op._abs, op._BIT, 4),
            0x2D: (op._abs, op._AND, 4), 0x2E: (op._abs, op._ROL, 6),
            0x30: (op._rel, op._BMI, 2), 0x31: (op._izy, op._AND, 5),
            0x35: (op._zpx, op._AND, 4), 0x36: (op._zpx, op._ROL, 6),
            0x38: (op._imp, op._SEC, 2), 0x39: (op._aby, op._AND, 4),
            0x3D: (op._abx, op._AND, 4), 0x3E: (op._abx, op._ROL, 7),
            0x48: (op._imp, op._PHA, 3), 0x50: (op._rel, op._BVC, 2),
            0x58: (op._imp, op._CLI, 2), 0x61: (op._izx, op._ADC, 6),
            0x65: (op._zpg, op._ADC, 3), 0x68: (op._imp, op._PLA, 4),
            0x69: (op._imm, op._ADC, 2), 0x6C: (op._ind, op._JMP, 5),
            0x6D: (op._abs, op._ADC, 4), 0x70: (op._rel, op._BVS, 2),
            0x71: (op._izy, op._ADC, 5), 0x75: (op._zpx, op._ADC, 4),
            0x78: (op._imp, op._SEI, 2), 0x79: (op._aby, op._ADC, 4),
            0x7D: (op._abx, op._ADC, 4), 0x81: (op._izx, op._STA, 6),
            0x84: (op._zpg, op._STY, 3), 0x85: (op._zpg, op._STA, 3),
            0x88: (op._imp, op._DEY, 2), 0x8A: (op._imp, op._TXA, 2),
            0x8C: (op._abs, op._STY, 4), 0x8D: (op._abs, op._STA, 4),
            0x90: (op._rel, op._BCC, 2), 0x91: (op._izy, op._STA, 6),
            0x94: (op._zpx, op._STY, 4), 0x95: (op._zpx, op._STA, 4),
            0x96: (op._zpy, op._STX, 4), 0x98: (op._imp, op._TYA, 2),
            0x99: (op._aby, op._STA, 5), 0x9A: (op._imp, op._TXS, 2),
            0x9D: (op._abx, op._STA, 5), 0xA0: (op._imm, op._LDY, 2),
            0xA1: (op._izx, op._LDA, 6), 0xA2: (op._imm, op._LDX, 2),
            0xA4: (op._zpg, op._LDY, 3), 0xA5: (op._zpg, op._LDA, 3),
            0xA6: (op._zpg, op._LDX, 3), 0xA8: (op._imp, op._TAY, 2),
            0xA9: (op._imm, op._LDA, 2), 0xAA: (op._imp, op._TAX, 2),
            0xAC: (op._abs, op._LDY, 4), 0xAD: (op._abs, op._LDA, 4),
            0xAE: (op._abs, op._LDX, 4), 0xB0: (op._rel, op._BCS, 2),
            0xB1: (op._izy, op._LDA, 5), 0xB4: (op._zpx, op._LDY, 4),
            0xB5: (op._zpx, op._LDA, 4), 0xB6: (op._zpy, op._LDX, 4),
            0xB8: (op._imp, op._CLV, 2), 0xB9: (op._aby, op._LDA, 4),
            0xBA: (op._imp, op._TSX, 2), 0xBC: (op._abx, op._LDY, 4),
            0xBD: (op._abx, op._LDA, 4), 0xBE: (op._aby, op._LDX, 4),
            0xC6: (op._zpg, op._DEC, 5), 0xC8: (op._imp, op._INY, 2),
            0xCA: (op._imp, op._DEX, 2), 0xCE: (op._abs, op._DEC, 6),
            0xD0: (op._rel, op._BNE, 2), 0xD6: (op._zpx, op._DEC, 6),
            0xD8: (op._imp, op._CLD, 2), 0xDE: (op._abx, op._DEC, 7),
            0xE1: (op._izx, op._SBC, 6), 0xE5: (op._zpg, op._SBC, 3),
            0xE6: (op._zpg, op._INC, 5), 0xE8: (op._imp, op._INX, 2),
            0xE9: (op._imm, op._SBC, 2), 0xED: (op._abs, op._SBC, 4),
            0xEE: (op._abs, op._INC, 6), 0xF0: (op._rel, op._BEQ, 2),
            0xF1: (op._izy, op._SBC, 5), 0xF5: (op._zpx, op._SBC, 4),
            0xF6: (op._zpx, op._INC, 6), 0xF8: (op._imp, op._SED, 2),
            0xF9: (op._aby, op._SBC, 4), 0xFD: (op._abx, op._SBC, 4),
            0xFE: (op._abx, op._INC, 7)
        }

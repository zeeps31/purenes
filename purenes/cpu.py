# Python 3.7 and 3.8 support
try:
    from typing import Final  # pragma: no cover
    from typing import TypedDict  # pragma: no cover
except ImportError:  # pragma: no cover
    from typing_extensions import Final  # pragma: no cover
    from typing_extensions import TypedDict  # pragma: no cover
import ctypes
from typing import List
from typing import Tuple
from typing import Callable
from typing import Dict


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
    """A class to represent the NES CPU core.

    The NES CPU is based on the MOS6502 processor and runs at approximately
    1.79 MHz.

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

        Active Opcode and Operation Value:
            :attr:`~purenes.cpu.CPU.opcode`
            :attr:`~purenes.cpu.CPU.operation_value`
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

    # The "effective address" is the address that contains the value needed
    # by the operation. The effective address is either formed from the
    # operand, or is the operand itself (E.g. absolute addressing).
    _effective_address: int

    # The internal bus for the CPU
    _cpu_bus: CPUBus

    # Tracks the total number of cycles that have been performed. This value
    # is used to synchronize the CPU and PPU
    _cycle_count: int = 0

    _operations:      Dict[int, Tuple[Callable, Callable]]
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

        Each time the CPU is clocked the following events occur:

        1. The CPU reads from :class:`~purenes.cpu.CPUBus` at the address
           stored in the program counter.
        2. The program counter is incremented by one.
        3. The operation retrieved from the address at the program counter is
           executed.

        Returns:
            None
        """
        self.opcode = self._read(self.pc)
        self.pc += 1

        self._load_operation()

        self._retrieve_operation_value()
        self._execute_operation()

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
        self._cycle_count += 7

    def _read(self, address: int) -> int:
        return self._cpu_bus.read(address)

    def _write(self, address: int, data: int) -> None:
        self._cpu_bus.write(address, data)

    def _load_operation(self) -> None:
        operation: Tuple[Callable, Callable] = self._operations[self.opcode]

        self._addressing_mode = operation[0]
        self._operation = operation[1]

    def _retrieve_operation_value(self):
        # Execute the addressing mode required by the current operation to
        # retrieve the operand.
        self._addressing_mode()

    def _execute_operation(self):
        # Perform the current operation.
        self._operation()

    def _imp(self):
        # Implied addressing mode. In this mode the operand is implied by the
        # operation.
        return

    # Addressing Modes

    def _izx(self):
        # X-indexed indirect addressing mode.

        # The operand is a zero-page address. This value is added with the x
        # register to form the effective address. This addressing mode wraps
        # around for values larger than $FF.
        operand: int = self._read(self.pc)
        self.pc += 1

        lo: int = self._read((operand + self.x) & 0x00FF)
        hi: int = self._read((operand + self.x + 1) & 0x00FF)

        self._effective_address = hi << 8 | lo
        self.operation_value = self._read(self._effective_address)

    def _zpg(self):
        # Zero page addressing mode. Address = $00LL.
        operand: int = self._read(self.pc)
        self._effective_address = operand
        self.operation_value = self._read(self._effective_address)
        self.pc += 1

    # Operations

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

        self._cycle_count += 7

    def _ORA(self):
        # OR with the accumulator.
        self.a |= self.operation_value

        # Sets the negative flag if the two's complement MSB is 1.
        self.status.flags.negative = (self.a & 0x80) != 0
        self.status.flags.zero = self.a == 0x00

    def _push_to_stack(self, data: int) -> None:
        # Push a value to the stack. The stack is implemented at addresses
        # $0100 - $01FF and is a LIFO stack. A push to the stack decrements the
        # stack pointer by 1.
        self._write(0x0100 | self.s, data)
        self.s -= 1

    def _map_operations(self) -> None:
        # Map operations and addressing modes to opcodes.
        op = self
        self._operations = {
            0x00:  (op._imp, op._BRK), 0x01: (op._izx, op._ORA),
            0x05:  (op._zpg, op._ORA),
        }

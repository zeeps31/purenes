# Python 3.7 and 3.8 support
try:
    from typing import Final
except ImportError:
    from typing_extensions import Final
from typing import List


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
    """
    # The internal bus for the CPU
    _cpu_bus: CPUBus

    # The low byte of the reset vector.
    _RES: int = 0xFFFC

    # CPU Internal registers
    _A: int
    _X: int
    _Y: int
    _PC: int

    # Tracks the total number of cycles that have been performed. This value
    # is used to synchronize the CPU and PPU
    _cycle_count: int = 0
    # Used to track the current opcode that the CPU is executing.
    _active_operation: int

    def __init__(self, cpu_bus: CPUBus):
        """Connect the :class:`~purenes.cpu.CPUBus` to the CPU.

        Note:
            None of the internal registers are initialized at this point. This
            does not happen until :func:`~purenes.cpu.CPU.reset` is called.

        Args:
            cpu_bus (CPUBus): An instance of a :class:`~purenes.cpu.CPUBus`
        """
        self._cpu_bus = cpu_bus

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
        self._active_operation = self._read(self._PC)
        self._PC += 1
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
        # Perform power-up state actions.
        self._A = 0x00
        self._X = 0x00
        self._Y = 0x00

        pc_lo: int = self._read(self._RES)
        pc_hi: int = self._read(self._RES + 1)

        self._PC = pc_hi << 8 | pc_lo

        # As the reset line goes high the processor performs a start sequence
        # of 7 cycles
        self._cycle_count += 7

    def _read(self, address: int) -> int:
        return self._cpu_bus.read(address)

    def _write(self, address: int, data: int) -> None:
        self._cpu_bus.write(address, data)

    def _execute_operation(self) -> None:
        pass

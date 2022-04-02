from purenes.cpu import CPUBus


class CPU(object):
    """A class to represent the NES CPU core.

    The NES CPU is based on the MOS6502 processor and runs at approximately
    1.79 MHz.

    Internal Registers:
    ------------------

    A - Accumulator:
        8-bit register that supports using the status register
        for carrying, overflow detection, and so on.

    X and Y indexes:
        8-bit registers used for several addressing modes. They can be used as
        loop counters easily, using INC/DEC and branch instructions.

    PC - Program Counter:
        16-bits supports 65536 direct (unbanked) memory locations, however not
        all values are sent to the cartridge. It can be accessed either by
        allowing CPU's internal fetch logic increment the address bus, an
        interrupt (NMI, Reset, IRQ/BRQ), and using the RTS/JMP/JSR/Branch
        instructions.

    S  - Stack Pointer:
        8-bit and can be accessed using interrupts, pulls, pushes and
        transfers.
    """
    # The internal bus for the CPU
    cpu_bus: CPUBus

    # The lo-byte of the reset vector.
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

        Notes
        -----
            None of the internal registers are initialized at this point. This
            does not happen until :func:`~purenes.cpu.CPU.reset` is called.

        Parameters
        ----------
            cpu_bus : CPUBus
                An instance of a :class:`~purenes.cpu.CPUBus`
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

        Returns
        -------
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

        Returns
        -------
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

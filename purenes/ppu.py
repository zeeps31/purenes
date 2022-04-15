# Python 3.7 and 3.8 support
try:
    from typing import Final  # pragma: no cover
except ImportError:  # pragma: no cover
    from typing_extensions import Final  # pragma: no cover
import ctypes
from typing import List


class _Control(ctypes.Union):
    """A class to represent the PPU $2000 register. The flags have been
    replaced with more readable alternatives. A mapping is provided below.

    Note:
        This class should only be directly accessed through the read-only
        :attr:`~purenes.ppu.PPU.control` property of the
        :class:`~purenes.ppu.PPU`. The documentation of this class is included
        as a reference for testing and debugging.

    https://www.nesdev.org/wiki/PPU_registers#PPUCTRL

    The values detailed below can be accessed using the
    :attr:`~purenes.ppu._Control.flags` attribute of this class.

    * base_nt_address (NN) - The the base nametable address (0 = $2000; 1 =
      $2400; 2 = $2800; 3 = $2C00).

    * vram_address_increment (I) - How the VRAM address should be incremented
      per CPU read/write (0: add 1, going across; 1: add 32, going down).

    * sprite_pt_address (S) - Sprite pattern table address for 8x8 sprites
      (0: $0000; 1: $1000; ignored in 8x16 mode).

    * background_pt_address (B) - Background pattern table address (0: $0000;
      1: $1000).

    * sprite_size (H) - Sprite size (0: 8x8 pixels; 1: 8x16 pixels)

    * ppu_leader_follower_select (P) - PPU leader/follower select (0: read
      backdrop from EXT pins; 1: output color on EXT pins)

    * generate_nmi (V) - Generate an NMI at the start of the vertical blanking
      interval (0: off; 1: on)
    """
    _fields_ = [
        ("flags", type(
            "_PPUCTRL",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("base_nt_address",            ctypes.c_uint8, 2),
                ("vram_address_increment",     ctypes.c_uint8, 1),
                ("sprite_pt_address",          ctypes.c_uint8, 1),
                ("background_pt_address",      ctypes.c_uint8, 1),
                ("sprite_size",                ctypes.c_uint8, 1),
                ("ppu_leader_follower_select", ctypes.c_uint8, 1),
                ("generate_nmi",               ctypes.c_uint8, 1),
            ]}
        )),
        ("reg", ctypes.c_uint8)]


class _Status(ctypes.Union):
    """A class to represent the PPUSTATUS $2002 register.

    Note:
        This class should only be directly accessed through the read-only
        :attr:`~purenes.ppu.PPU.status` property of the
        :class:`~purenes.ppu.PPU`. The documentation of this class is included
        as a reference for testing and debugging.

    The values detailed below can be accessed using the
    :attr:`~purenes.ppu._Status.flags` attribute of this class.

    https://www.nesdev.org/wiki/PPU_registers#PPUSTATUS

    * na (.....) - Unused

    * sprite_overflow (O) - Sprite overflow. Intended to be set when more than
      eight sprites appear on a scanline.

    * sprite_zero_hit (S) - Set when a nonzero pixel of sprite 0 overlaps a
      nonzero background pixel.

    * vertical_blank (V) - Vertical blank has started (0: not in vblank; 1: in
      vblank).
    """
    _fields_ = [
        ("flags", type(
            "_PPUSTATUS",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("na",              ctypes.c_uint8, 5),  # Unused
                ("sprite_overflow", ctypes.c_uint8, 1),
                ("sprite_zero_hit", ctypes.c_uint8, 1),
                ("vertical_blank",  ctypes.c_uint8, 1),
            ]}
        )),
        ("reg", ctypes.c_uint8)]


class _Address(ctypes.Union):
    """A class to represent the PPU $2006 register.

    Note:
        This class should only be directly accessed through the read-only
        :attr:`~purenes.ppu.PPU.vram` and :attr:`~purenes.ppu.PPU.vram_temp`
        properties of the :class:`~purenes.ppu.PPU`. The documentation of this
        class is included as a reference for testing and debugging.

    During writes from the CPU through $2006 this register behaves as a
    reference to the current nametable address to begin rendering from. The CPU
    performs two writes to this register (high byte first) to compose the full
    address.

    During rendering, however, this register is composed and utilized by the
    PPU in a different way.

    The PPU maintains two 15-bit registers for this.

    v - Current VRAM address (15 bits)

    t - Temporary VRAM address (15 bits)

    The 15-bit registers t and v are composed this way during rendering:

    ::

        yyy NN YYYYY XXXXX
        ||| || ||||| +++++-- coarse X scroll
        ||| || +++++-------- coarse Y scroll
        ||| ++-------------- nametable select
        +++----------------- fine Y scroll

    The values detailed above be accessed using the
    :attr:`~purenes.ppu._Address.flags` attribute of this class.

    * coarse_x (XXXXX) - The coarse X value to use when scrolling.

    * coarse_y (YYYYY) - The coarse Y value to use when scrolling.

    * nt_select (NN) - Nametable select.

    * fine_y (yyy) - The fine y value to use when scrolling.
    """
    _fields_ = [
        ("flags", type(
            "_PPUADDRESS",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("coarse_x",  ctypes.c_uint8, 5),
                ("coarse_y",  ctypes.c_uint8, 5),
                ("nt_select", ctypes.c_uint8, 2),
                ("fine_y",    ctypes.c_uint8, 3),
            ]}
        )),
        ("reg", ctypes.c_uint16)]


class PPUBus(object):
    """A class to encapsulate the logic of reading and writing to devices
    connected to the PPU.

    The PPU has its own bus with a 16kB addressable range, $0000-3FFF,
    completely separate from the CPU's address bus. The PPU interacts with its
    connected devices directly or via the CPU with memory mapped registers at
    $2006 and $2007.

    https://www.nesdev.org/wiki/PPU_memory_map

    +----------------+-------+-----------------------------------------------+
    | Address range  | Size  | Description                                   |
    +================+=======+===============================================+
    | $0000-$0FFF    | $1000 | Pattern table 0                               |
    | $1000-$1FFF    | $1000 | Pattern table 1                               |
    +----------------+-------+-----------------------------------------------+
    | $2000-$23FF    | $0400 | Nametable 0                                   |
    | $2400-$27FF    | $0400 | Nametable 1                                   |
    | $2800-$2BFF    | $0400 | Nametable 2                                   |
    | $2C00-$2FFF    | $0400 | Nametable 3                                   |
    +----------------+-------+-----------------------------------------------+
    | $3000-$3EFF    | $0F00 | Mirrors of $2000-$2EFF                        |
    +----------------+-------+-----------------------------------------------+
    | $3F00-$3F1F    | $0020 | Palette RAM indexes                           |
    | $3F20-$3FFF    | $00E0 | Mirrors of $3F00-$3F1F                        |
    +----------------+-------+-----------------------------------------------+
    """

    # TODO: https://github.com/zeeps31/purenes/issues/6
    _INVALID_ADDRESS_EXCEPTION: Final = ("Invalid address provided: "
                                         "{address}. Address should be "
                                         "between 0x0000 - 0x3FFF")

    _VRAM_ADDRESS_MASK: Final = 0x07FF

    # The 2KB video ram (VRAM) dedicated to the PPU, normally mapped to the
    # nametable address space from $2000-2FFF,
    _vram: List[int]

    def __init__(self):
        self._vram = [0x00] * 0x0800

    def read(self, address: int) -> int:
        """Reads a value from the appropriate resource connected to the PPU.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value from the specified address location.
        """
        # TODO: https://github.com/zeeps31/purenes/issues/14
        if 0x2000 <= address <= 0x2FFF:
            return self._vram[address & self._VRAM_ADDRESS_MASK]

        else:
            raise Exception(
                self._INVALID_ADDRESS_EXCEPTION.format(
                    address=hex(address)
                )
            )

    def write(self, address: int, data: int) -> None:
        """Writes a value from the appropriate resource connected to the PPU.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None
        """
        # TODO: https://github.com/zeeps31/purenes/issues/14
        if 0x2000 <= address <= 0x2FFF:
            self._vram[address & self._VRAM_ADDRESS_MASK] = data

        else:
            raise Exception(
                self._INVALID_ADDRESS_EXCEPTION.format(
                    address=hex(address)
                )
            )


class PPU(object):

    _REGISTER_ADDRESS_MASK: Final = 0x08

    # Internal registers
    _control = _Control()  # $2000
    _status = _Status()  # $2002

    # Loopy Registers
    _vram = _Address()       # Loopy v $2006
    _vram_temp = _Address()  # Loopy t
    _fine_x: int             # Loopy x fine x scroll
    _write_latch: int        # Loopy w latch (0 first write, 1 second)

    # $2007 read buffer used to preserve data across frames.
    _data_read_buffer: int

    _ppu_bus: PPUBus

    def __init__(self, ppu_bus: PPUBus):
        self._ppu_bus = ppu_bus

    def read(self, address: int) -> int:
        """Public read method exposed by the PPU for communication with the
        CPU through memory mapped registers $2000-$2007.

        Note:
            Although there are only eight registers, the values are mirrored
            every 8 bytes through $3FFF.

        Args:
            address (int): A 16-bit address

        Returns:
            int: An 8-bit value
        """
        if 0x2000 <= address <= 0x3FFF:
            _address = address % self._REGISTER_ADDRESS_MASK

            if _address == 0x0002:
                self._write_latch = 0
                return self._status.reg

            elif _address == 0x0007:
                address_increment = 1
                if self._control.flags.vram_address_increment == 1:
                    address_increment = 32

                # When reading while the VRAM address is in the range 0-$3EFF
                # the read will return the contents of an internal read buffer.
                # This internal buffer is updated only when reading PPUDATA
                data = self._data_read_buffer
                self._data_read_buffer = self._read(self._vram.reg)

                # Reading palette data from $3F00-$3FFF returns the
                # current result.
                if self._vram.reg >= 0x3F00:
                    data = self._data_read_buffer

                self._vram.reg += address_increment
                return data

    def write(self, address: int, data: int) -> None:
        """Public write method exposed by the PPU for communication with the
        CPU through memory mapped registers $2000-$2007.

        Note:
            Although there are only eight registers, the values are mirrored
            every 8 bytes through $3FFF.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None
        """
        if 0x2000 <= address <= 0x3FFF:
            _address = address % self._REGISTER_ADDRESS_MASK

            if _address == 0x0000:
                self._control.reg = data
                nt_select = self._control.flags.base_nt_address
                self._vram_temp.flags.nt_select = nt_select

            if _address == 0x0006:
                t = self._vram_temp.reg  # Preserve space
                if self._write_latch == 0:
                    # Set bits 8-13 of vram_temp. The bitwise AND with 0x3F
                    # isolates bits 0-5 and the bit shift << 8 moves the bits
                    # to 8-13. This effectively clears bit 9 (z) as required.
                    # The bitwise AND with 0x00FF low-order bits 0-7 preserves
                    # the current value.
                    self._vram_temp.reg = ((data & 0x3F) << 8) | (t & 0x00FF)
                    self._write_latch = 1

                else:
                    # Set low order bits 0-7 and perform bitwise OR with the
                    # high order bits assigned on the first write.
                    # Transfer t to v.
                    self._vram_temp.reg = (t & 0xFF00) | data
                    self._vram.reg = self._vram_temp.reg
                    self._write_latch = 0

    def reset(self) -> None:
        """Perform a reset of the PPU.

        Calling this method will reset a series of internal registers and
        values used for rendering.

        https://www.nesdev.org/wiki/PPU_power_up_state

        Returns:
            None
        """
        self._control.reg = 0x00
        self._status.reg = 0x00
        self._vram.reg = 0x00
        self._vram_temp.reg = 0x00
        self._write_latch = 0x00
        self._fine_x = 0x00
        self._data_read_buffer = 0x00

    @property
    def control(self) -> _Control:
        """Read-only access to the internal PPUCTRL register $2000. This should
        only be used for testing and debugging purposes

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            _Control: The internal Control register class
        """
        return self._control

    @property
    def status(self) -> _Status:
        """Read-only access to the internal PPUSTATUS register $2002. This
        should only be used for testing and debugging purposes

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            _Status: The internal Status register class
        """
        return self._status

    @property
    def vram(self) -> _Address:
        """Read-only access to the internal PPUADDR register $2006 (v).

        This should only be used for testing and debugging purposes.

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            _Address
        """
        return self._vram

    @property
    def vram_temp(self) -> _Address:
        """Read-only access to the internal PPUADDR register $2006 (t).

        This should only be used for testing and debugging purposes.

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            _Address
        """
        return self._vram_temp

    @property
    def write_latch(self) -> int:
        """Read-only access to the internal write latch (w).

        This should only be used for testing and debugging purposes.

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            int: (0 first write, 1 second)
        """
        return self._write_latch

    def _read(self, address: int) -> int:
        # Internal read.
        return self._ppu_bus.read(address)

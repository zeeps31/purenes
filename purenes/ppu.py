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

    * base_nt_address        (NN) - (0 = $2000; 1 =$2400; 2 = $2800; 3 = $2C00)
    * vram_address_increment (I) - (0: add 1, x; 1: add 32, y).
    * sprite_pt_address      (S) - (0: $0000; 1: $1000; ignored in 8x16 mode).
    * background_pt_address  (B) - (0: $0000; 1: $1000).
    * sprite_size            (H) - Sprite size (0: 8x8 pixels; 1: 8x16 pixels)
    * ppu_leader_follower    (P) - EXT pins (0: read backdrop; 1: output color)
    * generate_nmi           (V) - (0: off; 1: on)
    """
    _fields_ = [
        ("flags", type(
            "_PPUCTRL",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("base_nt_address",        ctypes.c_uint8, 2),
                ("vram_address_increment", ctypes.c_uint8, 1),
                ("sprite_pt_address",      ctypes.c_uint8, 1),
                ("background_pt_address",  ctypes.c_uint8, 1),
                ("sprite_size",            ctypes.c_uint8, 1),
                ("ppu_leader_follower",    ctypes.c_uint8, 1),
                ("generate_nmi",           ctypes.c_uint8, 1),
            ]}
        )),
        ("reg", ctypes.c_uint8)]


class _Mask(ctypes.Union):
    """A class to represent the PPUMASK $2001 register.

    Note:
        This class should only be directly accessed through the read-only
        :attr:`~purenes.ppu.PPU.mask` property of the
        :class:`~purenes.ppu.PPU`. The documentation of this class is included
        as a reference for testing and debugging.

    The values detailed below can be accessed using the
    :attr:`~purenes.ppu._Mask.flags` attribute of this class.

    https://www.nesdev.org/wiki/PPU_registers#PPUMASK

    * greyscale                (G) - (0: normal , 1: greyscale)
    * show_background_leftmost (m) - (1: show, 0: hide)
    * show_sprites_leftmost    (M) - (1: show , 0: hide)
    * show_background          (b) - (1: show background)
    * show_sprites             (s) - (1: show sprites)
    * emphasize_red            (R) - Emphasize red
    * emphasize_green          (G) - Emphasize green
    * emphasize_blue           (B) - Emphasize blue
    """
    _fields_ = [
        ("flags", type(
            "_PPUMASK",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("greyscale",                ctypes.c_uint8, 1),
                ("show_background_leftmost", ctypes.c_uint8, 1),
                ("show_sprites_leftmost",    ctypes.c_uint8, 1),
                ("show_background",          ctypes.c_uint8, 1),
                ("show_sprites",             ctypes.c_uint8, 1),
                ("emphasize_red",            ctypes.c_uint8, 1),
                ("emphasize_green",          ctypes.c_uint8, 1),
                ("emphasize_blue",           ctypes.c_uint8, 1),
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

    * na              (.....) - Unused
    * sprite_overflow (O) - Set when more than 8 sprites appear on a scanline.
    * sprite_zero_hit (S) - Pixel > 0 of sprite 0 overlaps a background pixel.
    * vertical_blank  (V) - (0: not in VBLANK; 1: in VBLANK).
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

    The values detailed below can be accessed using the
    :attr:`~purenes.ppu._Address.flags` attribute of this class.

    * coarse_x    (XXXXX) - The coarse X value to use when scrolling.
    * coarse_y    (YYYYY) - The coarse Y value to use when scrolling.
    * nt_select_x (N) - Horizontal nametable select.
    * nt_select_y (N) - Vertical nametable select.
    * fine_y      (yyy) - The fine y value to use when scrolling.
    """
    _fields_ = [
        ("flags", type(
            "_PPUADDRESS",
            (ctypes.LittleEndianStructure,),
            {"_fields_": [
                ("coarse_x",    ctypes.c_uint16, 5),
                ("coarse_y",    ctypes.c_uint16, 5),
                ("nt_select_x", ctypes.c_uint16, 1),
                ("nt_select_y", ctypes.c_uint16, 1),
                ("fine_y",      ctypes.c_uint16, 3),
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
    """A class to represent the NES Picture Processing Unit (PPU).

    This class is responsible for interacting with the
    :class:`~purenes.cpu.CPU` and devices connected to the
    :class:`~purenes.ppu.PPUBus` to generate a composite video signal with 240
    lines of pixels for each frame.

    https://www.nesdev.org/wiki/PPU
    """

    _REGISTER_ADDRESS_MASK: Final = 0x08

    # NTSC cycle and scanline maximums
    _MAX_SCANLINE: Final = 260
    _MAX_CYCLE: Final = 340

    # Internal registers
    _control = _Control()  # $2000
    _mask = _Mask()        # $2001
    _status = _Status()    # $2002

    # Loopy Registers
    _vram = _Address()       # Loopy v $2006
    _vram_temp = _Address()  # Loopy t
    _fine_x: int             # Loopy x fine x scroll
    _write_latch: int        # Loopy w latch (0 first write, 1 second)

    # $2007 read buffer used to preserve data across frames.
    _data_read_buffer: int

    # Internal latches used to store values before they are loaded into shift
    # registers
    _nametable_latch: int  # A nametable tile ID

    # Counters
    _scanline: int = -1  # Current scanline
    _cycle: int = 0      # Current cycle within a scanline

    _ppu_bus: PPUBus

    def __init__(self, ppu_bus: PPUBus):
        """Connect the :class:`~purenes.ppu.PPUBus` to the PPU.

        Note:
            None of the internal registers are initialized at this point. This
            does not happen until :func:`~purenes.ppu.PPU.reset` is called.

        Args:
            ppu_bus (PPUBus): An instance of a :class:`~purenes.ppu.PPUBus`
        """
        self._ppu_bus = ppu_bus

    def clock(self) -> None:
        """Perform one clock of the PPU.

        The action performed for each clock cycle is contingent upon the
        current scanline, cycle and state of the PPU.

        https://www.nesdev.org/wiki/PPU_rendering

        Returns:
            None
        """
        # Preserve space
        scanline = self._scanline
        cycle = self._cycle

        # Visible scanline (0-239).
        if -1 <= scanline <= 239:

            if cycle == 257:
                # Last cycle of visible scanline, reset coarse_x
                self._vram.flags.coarse_x = self._vram_temp.flags.coarse_x

            if (1 <= cycle <= 256) or (321 <= cycle <= 340):
                # Some of the rendering process repeats itself every 8 cycles
                # The process does not start until cycle 1, the rendering_cycle
                # value is decremented by 1 to improve readability.
                rendering_cycle = (cycle - 1) % 8
                if rendering_cycle == 0:
                    # 0x2000 + low 12-bits of (v)
                    nt_address: int = 0x2000 | (self._vram.reg & 0x0FFF)
                    self._nametable_latch = self._read(nt_address)

                elif rendering_cycle == 7:
                    (self._increment_y() if cycle == 256
                     else self._increment_coarse_x())

        self._increment_cycle()

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
                self._vram_temp.flags.nt_select_x = nt_select & 0x01
                self._vram_temp.flags.nt_select_y = (nt_select >> 1) & 0x01

            elif _address == 0x0001:
                self._mask.reg = data

            elif _address == 0x0005:
                t = self._vram_temp  # Preserve space
                if self._write_latch == 0:
                    # On the first write bits 3-7 are used to set coarse_x in
                    # vram_temp (t) by bit shifting the data value right by
                    # three bits. A bitwise AND is performed on the data value
                    # with 0x07 (00000111) to set the fine_x scroll.
                    t.flags.coarse_x = data >> 3
                    self._fine_x = data & 0x07
                    self._write_latch = 1

                else:
                    # Bits 3-7 are used to set coarse_y in vram_temp (t) by
                    # bit shifting the data value right by three bits. A
                    # bitwise AND is performed on the data value with 0x07
                    # (00000111) to set the fine_y scroll in vram_temp (t).
                    t.flags.coarse_y = data >> 3
                    t.flags.fine_y = data & 0x07
                    self._write_latch = 0

            elif _address == 0x0006:
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

            elif _address == 0x0007:
                # Preserve space
                i = self._control.flags.vram_address_increment

                # Writing to $2007 does not impact the internal
                # _data_read_buffer
                self._write(self._vram.reg, data)
                self._vram.reg += 1 if i == 0 else 32

    def reset(self) -> None:
        """Perform a reset of the PPU.

        Calling this method will reset a series of internal registers and
        values used for rendering.

        https://www.nesdev.org/wiki/PPU_power_up_state

        Returns:
            None
        """
        self._control.reg = 0x00
        self._mask.reg = 0x00
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
    def mask(self) -> _Mask:
        """Read-only access to the internal PPUMASK register $2001. This should
        only be used for testing and debugging purposes

        Accessing the register through this property will not impact any of
        the other registers, so it is safe to do so.

        Returns:
            _Mask: The internal Mask register class
        """
        return self._mask

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

        Returns:
            int: (0 first write, 1 second)
        """
        return self._write_latch

    @property
    def fine_x(self) -> int:
        """Read-only access to the internal fine x scroll value (x).

        This should only be used for testing and debugging purposes.

        Returns:
            int: The value of the fine x scroll
        """
        return self._fine_x

    @property
    def scanline(self) -> int:
        """Read-only access to the internal scanline counter.

        This should only be used for testing and debugging purposes.

        Returns:
            int: The value of the current scanline
        """
        return self._scanline

    @property
    def cycle(self) -> int:
        """Read-only access to the internal scanline cycle counter.

        This should only be used for testing and debugging purposes.

        Returns:
            int: The value of the current cycle within a scanline
        """
        return self._cycle

    def _read(self, address: int) -> int:
        # Internal read.
        return self._ppu_bus.read(address)

    def _write(self, address: int, data: int) -> None:
        # Internal write.
        return self._ppu_bus.write(address, data)

    def _increment_cycle(self):
        # Increment cycle and scanline, handle resets.
        if self._cycle == self._MAX_CYCLE:
            # This is the last cycle on this scanline, reset the counter
            # increment or reset the scanline.
            self._cycle = 0
            self._scanline = (self._scanline + 1
                              if self._scanline < self._MAX_SCANLINE
                              else -1)
        else:
            self._cycle += 1

    def _increment_coarse_x(self):
        # Increment coarse_x after every 8 cycles. If coarse_x reaches the
        # maximum number of tiles in the nametable, the lower bit of the
        # nametable_select value is inverted (wrapped around).
        if self._vram.flags.coarse_x == 31:
            self._vram.flags.coarse_x = 0
            self._vram.flags.nt_select_x ^= 1
        else:
            self._vram.flags.coarse_x += 1

    def _increment_y(self):
        # Increment fine_y after every 8 cycles. If fine_y > 7 it overflows to
        # coarse_y. If coarse_y exceeds the maximum number of vertical tiles
        # (29) the nametable wraps around.
        if self._vram.flags.fine_y < 7:
            self._vram.flags.fine_y += 1
        else:
            self._vram.flags.fine_y = 0

            if self._vram.flags.coarse_y == 29:
                self._vram.flags.coarse_y = 0
                # Wrap vertical nametable
                self._vram.flags.nt_select_y ^= 1
            # TODO: https://github.com/zeeps31/purenes/issues/48
            else:
                self._vram.flags.coarse_y += 1

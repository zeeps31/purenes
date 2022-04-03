# Python 3.7 and 3.8 support
try:
    from typing import Final
except ImportError:
    from typing_extensions import Final
from typing import List


class PPUBus(object):
    """A class to encapsulate the logic of reading and writing to
    devices connected to the PPU.

    The PPU has its own bus with a 16kB addressable range, $0000-3FFF,
    completely separate from the CPU's address bus. The PPU interacts
    with its connected devices directly or via the CPU with memory
    mapped registers at $2006 and $2007.

    https://www.nesdev.org/wiki/PPU_memory_map

    Address range	Size	Description
    $0000-$0FFF	    $1000	Pattern table 0
    $1000-$1FFF	    $1000	Pattern table 1
    $2000-$23FF	    $0400	Nametable 0
    $2400-$27FF	    $0400	Nametable 1
    $2800-$2BFF	    $0400	Nametable 2
    $2C00-$2FFF	    $0400	Nametable 3
    $3000-$3EFF	    $0F00	Mirrors of $2000-$2EFF
    $3F00-$3F1F	    $0020	Palette RAM indexes
    $3F20-$3FFF	    $00E0	Mirrors of $3F00-$3F1F

    Methods
    -------
    read(address: int) -> int:
        Reads an address from a device connected to the PPU bus.

    write(address: int, data: int) -> None:
        Writes to an address and device connected to the PPU bus.
    """

    # TODO: https://github.com/zeeps31/purenes/issues/6
    _INVALID_ADDRESS_EXCEPTION: Final = ("Invalid address provided: "
                                         "{address}. Address should be "
                                         "between 0x0000 - 0x3FFF")

    _VRAM_ADDRESS_MASK: Final = 0x07FF

    # The 2KB video ram (VRAM) dedicated to the PPU, normally mapped to
    # the nametable address space from $2000-2FFF,
    _vram: List[int]

    def __init__(self):
        self._vram = [0x00] * 0x0800

    def read(self, address: int) -> int:
        """Reads a value from the appropriate resource connected to the
        PPU.

        Parameters
        ----------
            address : int
                A 16-bit address

        Returns
        -------
            data (int): An 8-bit value from the specified address
            location.
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
        """Writes a value from the appropriate resource connected to the
        PPU.

        Parameters
        ----------
            address : int
                A 16-bit address

            data : int
                An 8-bit value

        Returns
        -------
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

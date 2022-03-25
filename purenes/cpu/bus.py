from typing import Final

import numpy as np


class CPUBus(object):
    """A class to represent the NES CPU bus.

    The CPU bus is responsible for handling the logic of delegating
    reads and writes to the correct resource connected to the CPU
    based on the CPU memory map

    https://www.nesdev.org/wiki/CPU_memory_map.

    Address range Size	Device
    $0000-$07FF	  $0800	2KB internal RAM
    $0800-$0FFF	  $0800	Mirrors of $0000-$07FF
    $1000-$17FF	  $0800
    $1800-$1FFF	  $0800
    $2000-$2007	  $0008	NES PPU registers
    $2008-$3FFF	  $1FF8	Mirrors of $2000-2007 (repeats every 8 bytes)
    $4000-$4017	  $0018	NES APU and I/O registers
    $4018-$401F	  $0008	APU and I/O functionality.
    $4020-$FFFF	  $BFE0	Cartridge space: PRG ROM, PRG RAM, and mapper

    Methods
    -------
    read(address: np.uint16) -> np.uint8:
        Reads an address from a device connected to the CPU bus.

    write(address: np.uint16, data: np.uint8) -> None:
        Writes to an address and device connected to the CPU bus.
    """
    # TODO: https://github.com/zeeps31/purenes/issues/6
    _INVALID_ADDRESS_EXCEPTION: Final = ("Invalid address provided: "
                                         "{address}. Address should be " 
                                         "between 0x0000 - 0xFFFF")

    _RAM_ADDRESS_MASK: Final = 0x1FF

    _ram: np.array(np.uint8)

    def __init__(self):
        """
        'Connects' devices to the CPU and initializes the devices based
        on reset and startup behaviors.
        """
        # Internal memory ($0000-$07FF) has unreliable startup state.
        # Some machines may have consistent RAM contents at power-on,
        # but others do not. Here, the ram is initialized to a 2KB
        # array of 0x00 values.
        self._ram = np.zeros(0x07FF, np.uint8)

    def read(self, address: np.uint16) -> np.uint8:
        """
        Reads a value from the appropriate resource connected to the
        CPU.

        Parameters
        ----------
            address : np.uint16
                A 16-bit address

        Returns
        -------
            data (np.unit8): A value from the specified address
            location.
        """
        if 0x0000 <= address <= 0x1FFF:
            return self._ram[address & self._RAM_ADDRESS_MASK]

        else:
            raise Exception(
                self._INVALID_ADDRESS_EXCEPTION.format(
                    address=hex(address)
                )
            )

    def write(self, address: np.uint16, data: np.uint8) -> None:
        """
        Writes a value from the appropriate resource connected to the
        CPU.

        Parameters
        ----------
            address : np.uint16
                A 16-bit address

            data : np.uint8
                An 8-bit value

        Returns
        -------
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

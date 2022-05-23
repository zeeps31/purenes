import abc

import purenes.rom


class Mapper(abc.ABC):
    """An abstract mapper to provide common functionality required by all
    mappers. All mappers should inherit from this mapper.

    Attributes:
        rom (:class:`~purenes.rom.Rom`): Implementing classes should use the
             :attr:`~purenes.rom.Rom.read_prg_rom` and
             :attr:`~purenes.rom.Rom.read_chr_rom` methods to read data from
             the ROM using a mapped addresses
    """
    name: str

    def __init__(self, rom: purenes.rom.Rom):
        self.rom: purenes.rom.Rom = rom

    @abc.abstractmethod
    def cpu_read(self, address: int) -> int:
        """Read from PRG ROM or RAM using the appropriate mapping strategy.

        All implementing classes are required to implement this method.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """

    def cpu_write(self, address: int, data: int) -> None:
        """Write to PRG RAM or internal registers using the appropriate mapping
        strategy.

        Not all subclasses are required to implement this method.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None

        Raises:
            RuntimeError: Thrown if the CPU attempts to write to the Mapper but
                          this method is not implemented.
        """
        raise RuntimeError("The CPU attempted to write to PRG memory, but "
                           "writes to PRG memory are not supported or "
                           "implemented correctly by this Mapper.")

    @abc.abstractmethod
    def ppu_read(self, address: int) -> int:
        """Read from CHR ROM or RAM using the appropriate mapping strategy.

        All implementing classes are required to implement this method.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """

    def ppu_write(self, address: int, data: int) -> None:
        """Write to CHR RAM or internal registers using the appropriate mapping
        strategy.

        Not all subclasses are required to implement this method.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None

        Raises:
            RuntimeError: Thrown if the PPU attempts to write to the Mapper but
                          this method is not implemented.
        """
        raise RuntimeError("The PPU attempted to write to CHR memory, but "
                           "writes to CHR memory are not supported or "
                           "implemented correctly by this Mapper.")


from purenes.mappers.mapper0 import Mapper0
from typing import Dict
from typing import Type

SUPPORTED_MAPPERS: Dict[int, Type[Mapper]] = {
    0: Mapper0
}

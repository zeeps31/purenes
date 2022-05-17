try:
    from typing import TypedDict  # pragma: no cover
except ImportError:  # pragma: no cover
    from typing_extensions import TypedDict  # pragma: no cover

from typing import Type

from purenes.mappers import Mapper
from purenes.mappers import SUPPORTED_MAPPERS
from purenes.rom import Header
from purenes.rom import Mirroring
from purenes.rom import Rom


class CartridgeReadOnlyValues(TypedDict):
    """Read-only container of Cartridge internal values.

    This class should only be used for testing and debugging purposes.
    """
    header:      Header
    mapper_name: str


class Cartridge(object):
    """A class to represent a NES cartridge.

    The Cartridge class is a layer of abstraction around a Mapper. It receives
    reads and writes from the CPU and PPU and delegates to the active Mapper to
    perform the operation. The Cartridge, therefore, never accesses PRG and CHR
    ROM (or RAM if supported by the Mapper) directly but instead relies on the
    configuration and capabilities of the active Mapper to do so.

    The separate read/write methods for the CPU and PPU are based on the pinout
    of a NES cartridge connector. The cartridge connector pins were connected
    directly to the CPU and PPU address and data buses.

    https://www.nesdev.org/wiki/Cartridge_connector.

    Attributes:
        nt_mirroring (Mirroring): The nametable mirroring mode used by the
                                  Mapper.
    """

    def __init__(self, mapper: Mapper):
        self._mapper = mapper
        self.nt_mirroring = mapper.rom.header.nt_mirroring

    @classmethod
    def from_file(cls, file_path: str):
        """Load a ROM from a file path and create a Cartridge.

        Raises:
            RuntimeException: Thrown if the ROM requires a Mapper that is not
                              currently supported.
        """
        rom_data: bytes = open(file_path, "rb").read()
        rom: Rom = Rom(rom_data)

        try:
            _mapper: Type[Mapper] = SUPPORTED_MAPPERS[rom.header.mapper_id]
            mapper: Mapper = _mapper(rom)

        except KeyError:
            raise RuntimeError("The ROM provided uses iNES Mapper: "
                               "{mapper_id}. This Mapper is not currently "
                               "supported."
                               .format(mapper_id=rom.header.mapper_id))
        
        return cls(mapper)

    def cpu_read(self, address: int) -> int:
        """Read PRG data from the Mapper used by this Cartridge.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        return self._mapper.cpu_read(address)

    def cpu_write(self, address: int, data: int) -> None:
        """Write to PRG RAM or internal registers used by the active Mapper.

        Args:
            address (int): A 16-bit address
            data (int): An 8-bit value

        Returns:
            None
        """
        self._mapper.cpu_write(address, data)

    def ppu_read(self, address: int) -> int:
        """Read CHR data from the Mapper used by this Cartridge.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        return self._mapper.ppu_read(address)

    def ppu_write(self, address: int, data: int) -> None:
        """Write to CHR RAM or internal registers used by the active Mapper.

       Args:
           address (int): A 16-bit address
           data (int): An 8-bit value

       Returns:
           None
       """
        self._mapper.ppu_write(address, data)

    @property
    def read_only_values(self) -> CartridgeReadOnlyValues:
        """Read-only access to internal values for testing and debugging.
        """
        return {
            "header": self._mapper.rom.header,
            "mapper_name": self._mapper.name
        }

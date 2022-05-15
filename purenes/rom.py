from enum import Enum


class Mirroring(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class Header(object):
    """A class to represent an iNES header https://www.nesdev.org/wiki/INES

    Takes a .nes ROM file, parses the header from the bytes in the ROM file
    and exposes a set of values through instance attributes.

    Attributes:
        prg_banks (int): The number of program banks supported by this ROM
        chr_banks (int): The number of character banks supported by this ROM
        prg_rom_size (int): The size of the program rom in bytes
        chr_rom_size (int): The size of the character rom in bytes

        nt_mirroring (:class:`~purenes.rom.Mirroring`):  Nametable mirroring
                     configuration. Some Mappers ignore this value and
                     dynamically adjust the mirroring configuration during
                     gameplay.
        trainer (int): 512-byte trainer at $7000-$71FF (stored before PRG data)
        mapper_id (int): The id of the Mapper

    Raises:
        RuntimeError: Thrown if an invalid file type is provided.
    """

    def __init__(self, rom_data: bytes):
        header = rom_data[0: 16]
        ines_header = [0x4E, 0x45, 0x53, 0x1A]
        mapper_id: int

        # iNES header type 1
        if not all([header[i] == ines_header[i] for i in range(0, 4)]):

            raise RuntimeError("Invalid iNES Header. This is not a valid .nes "
                               "file or this file format is unsupported.")

        self.prg_banks: int = header[4]
        self.chr_banks: int = header[5]
        self.prg_rom_size: int = 16384 * self.prg_banks
        self.chr_rom_size: int = 8192 * self.chr_banks

        self.nt_mirroring: int = Mirroring(header[6] & 0x01)
        self.trainer: int = header[6] & 4
        self.mapper_id = header[7] & 0xF0 | header[6] >> 4


class Rom(object):
    """A class to represent an .nes ROM file.

    Exposes a set of read methods that can be used by mappers to access program
    and character read-only memory directly.

    Attributes:
        header (:class:`~purenes.rom.Header`): The iNES header for this ROM
    """
    _prg_rom: bytes  # The program rom
    _chr_rom: bytes  # The character rom

    def __init__(self, rom_data: bytes):
        self.header: Header = Header(rom_data)

        trainer_offset: int = 512 if self.header.trainer else 0
        prg_data_offset: int = 16 + trainer_offset
        chr_data_offset: int = prg_data_offset + self.header.prg_rom_size

        self._prg_rom: bytes = rom_data[prg_data_offset: chr_data_offset]
        self._chr_rom: bytes = rom_data[chr_data_offset: chr_data_offset +
                                        self.header.chr_rom_size]

    def read_prg_rom(self, address: int) -> int:
        """Read program data from the PRG ROM.

        This method should be used by Mappers to access the program ROM.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        return self._prg_rom[address]

    def read_chr_rom(self, address: int) -> int:
        """Read character data from the CHR ROM.

        This method should be used by Mappers to access the character ROM.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        return self._chr_rom[address]

from purenes.mappers import Mapper


class Mapper0(Mapper):
    """Class to represent iNES Mapper0 (NROM).

    NROM refers to the Nintendo cartridge boards NES-NROM-128, NES-NROM-256,
    their HVC counterparts, and clone boards. The iNES format assigns mapper
    0 to NROM.

    In this Mapper all banks are fixed. The program is mapped into $8000-$FFFF
    (NROM-256) or both $8000-$BFFF and $C000-$FFFF (NROM-128). The designation
    between the two is determined by :attr:`~purenes.rom.Header.prg_banks`.
    """

    name = "NROM"

    def ppu_read(self, address: int) -> int:
        """Read bytes from the CHR ROM.

        Mapper0 does not provide any mapping functionality for reads to CHR
        ROM. Calling this method will simply read the data at the address
        provided.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        return self.rom.read_chr_rom(address)

    def cpu_read(self, address: int) -> int:
        """Read bytes from the PRG ROM.

        If there are 2 program banks on the ROM the address is mapped into
        addresses $8000-$FFFF. If there is only 1 program bank the mapper
        treats addresses $C000-$FFFF as mirrors of $8000-$BFFF.

        Args:
            address (int): A 16-bit address

        Returns:
            data (int): An 8-bit value
        """
        prg_banks: int = self.rom.header.prg_banks
        _address = address & 0x7FFF if prg_banks == 2 else address & 0x3FFF
        return self.rom.read_prg_rom(_address)

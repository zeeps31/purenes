import pytest

from purenes.rom import Rom
from purenes.rom import Header
from purenes.rom import Mirroring


class TestRom(object):

    @pytest.fixture()
    def rom_data(self) -> bytes:
        h: bytes = b'NES\x1a\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        h += b'\x00' * (32768 + 8192)  # Dummy data PRG size + CHR size
        yield h

    def test_header_is_extracted_correctly(self, rom_data):
        """Tests that header data is correctly extracted from the header bytes.
        """
        rom: Rom = Rom(rom_data)

        header: Header = rom.header
        assert header.chr_banks == 1
        assert header.chr_rom_size == 8192
        assert header.mapper_id == 0
        assert header.nt_mirroring == Mirroring.VERTICAL
        assert header.prg_banks == 2
        assert header.prg_rom_size == 32768
        assert header.trainer == 0

    def test_loading_a_file_fails_for_incorrect_file_type(self):
        """Tests that the correct exception is thrown when an incorrect header
        is loaded into a ROM.
        """
        invalid_header: bytes = b'\x00\x00\x00\x00'

        with pytest.raises(RuntimeError) as exception:
            Rom(invalid_header)

        assert str(exception.value) == ("Invalid iNES Header. This is not a "
                                        "valid .nes file or this file format "
                                        "is unsupported.")

    def test_read_from_prg_rom(self, rom_data):
        """Tests that reads to CHR ROM return the correct values.

        Calls read_prg_rom with last value in the PRG ROM and verifies the
        correct data is returned.
        """
        rom: Rom = Rom(rom_data)

        data: int = rom.read_prg_rom(0x7FFF)

        assert data == 0x00

    def test_read_from_chr_rom(self, rom_data):
        """Tests that reads to CHR ROM return the correct values.

        Calls read_chr_rom with last value in the CHR ROM and verifies the
        correct data is returned.
        """
        rom: Rom = Rom(rom_data)

        data: int = rom.read_chr_rom(0x1FFF)

        assert data == 0x00

import pytest

import purenes.rom


def test_header_is_extracted_correctly(rom_data: bytes):
    """Tests that header data is correctly extracted from the header bytes.
    """
    rom: purenes.rom.Rom = purenes.rom.Rom(rom_data)

    header: purenes.rom.Header = rom.header
    assert header.chr_banks == 1
    assert header.chr_rom_size == 8192
    assert header.mapper_id == 0
    assert header.nt_mirroring == purenes.rom.Mirroring.VERTICAL
    assert header.prg_banks == 2
    assert header.prg_rom_size == 32768
    assert header.trainer == 0


def test_loading_a_file_fails_for_incorrect_file_type():
    """Tests that the correct exception is thrown when an incorrect header
    is loaded into a ROM.
    """
    invalid_header: bytes = b'\x00\x00\x00\x00'

    with pytest.raises(RuntimeError) as exception:
        purenes.rom.Rom(invalid_header)

    assert str(exception.value) == ("Invalid iNES Header. This is not a "
                                    "valid .nes file or this file format "
                                    "is unsupported.")


def test_read_from_prg_rom(rom_data: bytes):
    """Tests that reads to CHR ROM return the correct values.

    Calls read_prg_rom with last value in the PRG ROM and verifies the
    correct data is returned.
    """
    rom: purenes.rom.Rom = purenes.rom.Rom(rom_data)

    data: int = rom.read_prg_rom(0x7FFF)

    assert data == 0x00


def test_read_from_chr_rom(rom_data: bytes):
    """Tests that reads to CHR ROM return the correct values.

    Calls read_chr_rom with last value in the CHR ROM and verifies the
    correct data is returned.
    """
    rom: purenes.rom.Rom = purenes.rom.Rom(rom_data)

    data: int = rom.read_chr_rom(0x1FFF)

    assert data == 0x00

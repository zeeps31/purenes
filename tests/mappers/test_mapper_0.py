from unittest import mock

import pytest

from purenes import mappers


@pytest.fixture()
def mapper(mock_rom: mock.Mock):
    yield mappers.Mapper0(mock_rom)


def test_cpu_write_is_unsupported(
        mock_rom: mock.Mock,
        mapper: mappers.Mapper0):
    """Tests that writes from the CPU are not supported and throw an
    exception.
    """

    with pytest.raises(RuntimeError):
        mapper.cpu_write(0x00, 0x00)


def test_ppu_write_is_unsupported(
        mock_rom: mock.Mock,
        mapper: mappers.Mapper0):
    """Tests that writes from the PPU are not supported and throw an
    exception.
    """

    with pytest.raises(RuntimeError):
        mapper.ppu_write(0x00, 0x00)


def test_cpu_read_with_multiple_prg_banks_does_not_mirror_address(
        mock_header: mock.Mock,
        mock_rom: mock.Mock,
        mapper: mappers.Mapper0):
    """Tests addresses are mapped into addresses $8000-$FFFF if there are
    2 program banks on the ROM.

    Calls the cpu_read method of the mapper for address 0xCOOO and verifies
    that the mapper called read_prg_rom method of the ROM with address
    0x4000 (16383 + 1 i.e. the size of one prg bank + 1)
    """
    mock_header.prg_banks = 2

    mapper.cpu_read(0xC000)

    mock_rom.read_prg_rom.assert_called_with(0x4000)


def test_cpu_read_with_a_single_prg_bank_mirrors_address(
        mock_header: mock.Mock,
        mock_rom: mock.Mock,
        mapper: mappers.Mapper0):
    """Tests addresses are mirrored for addresses $C000-$FFFF if there is
    1 program bank on the ROM.

    Calls the cpu_read method of the mapper for address 0xCOOO and verifies
    that the mapper called read_prg_rom method of the ROM with address
    0x0000 (i.e. the address was mirrored back to 0)
    """
    mock_header.prg_banks = 1

    mapper.cpu_read(0xC000)

    mock_rom.read_prg_rom.assert_called_with(0x0000)


def test_ppu_read_does_not_map_address(
        mock_rom: mock.Mock,
        mapper: mappers.Mapper0):
    """Tests that the ppu_read method does not provide any mapping
    functionality.

    Calls the ppu_read method of the mapper for address 0x0000 and verifies
    that the mapper called read_chr_rom method of the ROM with the address
    provided.
    """
    mapper.ppu_read(0x0000)

    mock_rom.read_chr_rom.assert_called_with(0x0000)

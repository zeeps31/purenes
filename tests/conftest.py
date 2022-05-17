import pytest

from pytest_mock import MockFixture
from unittest.mock import Mock


@pytest.fixture()
def rom_data() -> bytes:
    rom: bytes = b'NES\x1a\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    rom += b'\x00' * (32768 + 8192)  # Dummy data PRG size + CHR size
    yield rom


@pytest.fixture()
def mock_header(mocker: MockFixture):
    """A Mock to represent a Header."""
    yield mocker.Mock()


@pytest.fixture()
def mock_rom(mocker: MockFixture, mock_header: Mock):
    """A Mock to represent a Rom with a mocked Header."""
    rom: Mock = mocker.Mock()
    rom.header = mock_header

    yield rom

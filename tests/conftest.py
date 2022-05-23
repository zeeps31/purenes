from unittest import mock

import pytest
import pytest_mock


@pytest.fixture()
def rom_data() -> bytes:
    rom: bytes = b'NES\x1a\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    rom += b'\x00' * (32768 + 8192)  # Dummy data PRG size + CHR size
    yield rom


@pytest.fixture()
def mock_header(mocker: pytest_mock.MockFixture):
    """A Mock to represent a Header."""
    yield mocker.Mock()


@pytest.fixture()
def mock_rom(mocker: pytest_mock.MockFixture, mock_header: mock.Mock):
    """A Mock to represent a Rom with a mocked Header."""
    rom: mock.Mock = mocker.Mock()
    rom.header = mock_header

    yield rom

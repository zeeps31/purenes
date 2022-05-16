import pytest
from pytest_mock import MockFixture

from unittest.mock import Mock


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

from unittest import mock

import pytest
import pytest_mock

import purenes.ppu


@pytest.fixture()
def ppu_bus():
    """A PPUBus instance."""
    ppu_bus: purenes.ppu.PPUBus = purenes.ppu.PPUBus()
    yield ppu_bus


@pytest.fixture()
def mock_ppu_bus(mocker: pytest_mock.MockFixture):
    """A Mock to represent the PPUBus."""
    mock_ppu_bus: mock.Mock = mocker.Mock()
    mock_ppu_bus.read.return_value = 0x00  # Default return value
    yield mock_ppu_bus


@pytest.fixture()
def ppu(mock_ppu_bus: mock.Mock):
    """A PPU instance with a mocked PPUBus."""
    yield purenes.ppu.PPU(mock_ppu_bus)


@pytest.fixture(autouse=True)
def before_each(ppu: purenes.ppu.PPU):
    """Reset the PPU between tests so that tests do not interfere with
    each other.
    """
    ppu.reset()

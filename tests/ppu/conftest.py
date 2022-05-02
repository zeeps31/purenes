from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture

from purenes.ppu import PPU
from purenes.ppu import PPUBus


@pytest.fixture()
def ppu_bus():
    """A PPUBus instance."""
    ppu_bus: PPUBus = PPUBus()
    yield ppu_bus


@pytest.fixture()
def mock_ppu_bus(mocker: MockFixture):
    """A Mock to represent the PPUBus."""
    mock_ppu_bus: Mock = mocker.Mock()
    mock_ppu_bus.read.return_value = 0x00  # Default return value
    yield mock_ppu_bus


@pytest.fixture()
def ppu(mock_ppu_bus: Mock):
    """A PPU instance with a mocked PPUBus."""
    yield PPU(mock_ppu_bus)


@pytest.fixture(autouse=True)
def before_each(ppu: PPU):
    """Reset the PPU between tests so that tests do not interfere with
    each other.
    """
    ppu.reset()

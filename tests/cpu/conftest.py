import pytest
from pytest_mock import MockFixture

from purenes.cpu import CPUBus


@pytest.fixture()
def cpu_bus():
    """A CPUBus instance."""
    cpu_bus: CPUBus = CPUBus()
    yield cpu_bus


@pytest.fixture()
def mock_cpu_bus(mocker: MockFixture):
    """A Mock to represent the CPUBus."""
    yield mocker.Mock()

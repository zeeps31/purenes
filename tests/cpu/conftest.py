from unittest import mock

import pytest
import pytest_mock

import purenes.cpu


@pytest.fixture()
def cpu_bus():
    """A CPUBus instance."""
    cpu_bus: purenes.cpu.CPUBus = purenes.cpu.CPUBus()
    yield cpu_bus


@pytest.fixture()
def mock_cpu_bus(mocker: pytest_mock.MockFixture):
    """A Mock to represent the CPUBus."""
    yield mocker.Mock()


@pytest.fixture()
def cpu(mock_cpu_bus: mock.Mock):
    """A CPU instance with a mocked CPUBus."""
    yield purenes.cpu.CPU(mock_cpu_bus)

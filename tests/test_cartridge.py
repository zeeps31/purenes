import math
from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture

from purenes.cartridge import Cartridge


class TestCartridge(object):

    @pytest.fixture()
    def mock_mapper(self, mocker: MockFixture):
        """A Mock to represent a Mapper."""
        yield mocker.Mock()

    @pytest.fixture()
    def cartridge(self, mock_mapper):
        """A Cartridge with a mocked Mapper"""
        yield Cartridge(mock_mapper)

    def test_from_file_creates_class_correctly(
            self,
            rom_data: bytes,
            mocker: MockFixture):
        """Tests that the from_file factory method generates a Cartridge as
        expected.

        Patches the open method and verifies that mocked open function was
        called with the correct file path and the mapper was loaded correctly.
        """
        mock_open = mocker.mock_open(read_data=rom_data)
        mocker.patch("builtins.open", mock_open)

        cartridge = Cartridge.from_file("test")

        assert isinstance(cartridge, Cartridge)
        mock_open.assert_called_with("test", "rb")

        assert cartridge.read_only_values["header"].mapper_id == 0

    def test_from_file_with_unsupported_mapper_fails(
            self,
            rom_data: bytes,
            mocker: MockFixture,
            mock_rom: Mock,
            mock_header: Mock
    ):
        """Tests that loading a Cartridge with an unsupported Mapper throws an
        exception with the correct exception message.
        """
        unsupported_mapper_id = math.inf
        mock_header.mapper_id = unsupported_mapper_id

        mock_open = mocker.mock_open(read_data=rom_data)
        mocker.patch("builtins.open", mock_open)
        mocker.patch("purenes.cartridge.Rom", return_value=mock_rom)

        with pytest.raises(RuntimeError) as exception:
            Cartridge.from_file("test")

        assert str(exception.value) == ("The ROM provided uses iNES Mapper: "
                                        "{mapper_id}. This Mapper is not "
                                        "currently supported.".format(
                                         mapper_id=unsupported_mapper_id))

    def test_cpu_read(self, cartridge, mock_mapper):
        """Tests that the Cartridge delegates cpu_read to the
        Mapper.
        """
        cartridge.cpu_read(0x0000)

        mock_mapper.cpu_read.assert_called_with(0x0000)

    def test_cpu_write(self, cartridge, mock_mapper):
        """Tests that the Cartridge delegates cpu_write to the
        Mapper.
        """
        cartridge.cpu_write(0x0000, 0x00)

        mock_mapper.cpu_write.assert_called_with(0x0000, 0x00)

    def test_ppu_read(self, cartridge, mock_mapper):
        """Tests that the Cartridge delegates ppu_read to the
        Mapper.
        """
        cartridge.ppu_read(0x0000)

        mock_mapper.ppu_read.assert_called_with(0x0000)

    def test_ppu_write(self, cartridge, mock_mapper):
        """Tests that the Cartridge delegates ppu_write to the
        Mapper.
        """
        cartridge.ppu_write(0x0000, 0x00)

        mock_mapper.ppu_write.assert_called_with(0x0000, 0x00)

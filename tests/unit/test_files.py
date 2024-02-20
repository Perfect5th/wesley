"""Unit tests for the wesley file-handling logic.

Copyright © 2024 Mitch Burton

This file is part of wesley.

wesley is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

wesley is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with wesley. If
not, see <https://www.gnu.org/licenses/>.
"""
import pathlib
from unittest import mock

from wesley import files, settings


def test_file_object_from_path() -> None:
    """Tests that `FileObject.from_path` results in the appropriate kind of file."""
    mock_settings = settings.Settings(pathlib.Path(''))

    markdown_file_object = files.FileObject.from_path(
        pathlib.Path('pixie.md'), mock_settings
    )

    assert isinstance(markdown_file_object, files.MarkdownFileObject)
    assert markdown_file_object.path == pathlib.Path('pixie.md')

    generic_file_object = files.FileObject.from_path(
        pathlib.Path('parsnip.txt'), mock_settings
    )

    assert isinstance(generic_file_object, files.GenericFileObject)


def test_generic_file_object_write(monkeypatch) -> None:
    """Tests that `GenericFileObject.write` results in a new file written in the target
    directory at the same relative location."""
    mock_settings = settings.Settings(pathlib.Path())
    mkdir_mock = mock.Mock(spec=pathlib.Path().mkdir)
    read_bytes_mock = mock.Mock(spec=pathlib.Path().read_bytes, return_value=b'elric\n')
    write_bytes_mock = mock.Mock(spec=pathlib.Path().write_bytes)

    monkeypatch.setattr(pathlib.Path, 'mkdir', mkdir_mock)
    monkeypatch.setattr(pathlib.Path, 'read_bytes', read_bytes_mock)
    monkeypatch.setattr(pathlib.Path, 'write_bytes', write_bytes_mock)

    generic_file_object = files.GenericFileObject(
        pathlib.Path('./site/here/there/everywhere.txt'), mock_settings
    )
    generic_file_object.write()

    mkdir_mock.assert_called_once_with(exist_ok=True)
    write_bytes_mock.assert_called_once_with(b'elric\n')

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
import io
import pathlib
import textwrap
from unittest import mock

import jinja2

import pytest

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


def test_generic_file_object_write_error(monkeypatch) -> None:
    """`GenericFileObject.write` raises a `FileObjectException` when there is an error."""
    mock_settings = settings.Settings(pathlib.Path())
    mkdir_mock = mock.Mock(spec=pathlib.Path().mkdir, side_effect=OSError('dag-nabbit'))
    read_bytes_mock = mock.Mock(
        spec=pathlib.Path().read_bytes, return_value=b'hawkeye\n'
    )
    write_bytes_mock = mock.Mock(spec=pathlib.Path().write_bytes)

    monkeypatch.setattr(pathlib.Path, 'mkdir', mkdir_mock)
    monkeypatch.setattr(pathlib.Path, 'read_bytes', read_bytes_mock)
    monkeypatch.setattr(pathlib.Path, 'write_bytes', write_bytes_mock)

    generic_file_object = files.GenericFileObject(
        pathlib.Path('./site/here/there/anywhere.txt'), mock_settings
    )

    with pytest.raises(files.FileObjectException) as exc_info:
        generic_file_object.write()

    mkdir_mock.assert_called_once_with(exist_ok=True)
    read_bytes_mock.assert_not_called()
    write_bytes_mock.assert_not_called()

    assert 'dag-nabbit' in str(exc_info.value)


def test_markdown_file_object_write(monkeypatch) -> None:
    """`MarkdownFileObject.write` results in a new HTML file written in the target
    directory at the same relative location, using information from the file's TOML
    header."""
    markdown_file_mock = io.StringIO()
    path_mock = mock.Mock(spec=pathlib.Path('./site/here/there/somewhere.md'))
    path_mock.name = './somewhere.md'
    path_mock.open.return_value = markdown_file_mock
    settings_mock = settings.Settings(path_mock)
    mkdir_mock = mock.Mock(spec=pathlib.Path().mkdir)
    write_text_mock = mock.Mock(spec=pathlib.Path().write_text)

    markdown_file_object = files.MarkdownFileObject(path_mock, settings_mock)

    read_toml_header_mock = mock.Mock(
        spec=markdown_file_object.read_toml_header,
        return_value={'title': 'Tiny Dogs', 'template': 'root.html'},
    )
    render_mock = mock.Mock(spec=markdown_file_object.render)

    monkeypatch.setattr(markdown_file_object, 'read_toml_header', read_toml_header_mock)
    monkeypatch.setattr(
        files.FileObject, 'target_dir', pathlib.Path('./_site/here/there')
    )
    monkeypatch.setattr(pathlib.Path, 'mkdir', mkdir_mock)
    monkeypatch.setattr(pathlib.Path, 'write_text', write_text_mock)
    monkeypatch.setattr(markdown_file_object, 'render', render_mock)

    markdown_file_object.write()

    mkdir_mock.assert_called_once_with(exist_ok=True)
    path_mock.open.assert_called_once()
    read_toml_header_mock.assert_called_once_with(markdown_file_mock)
    render_mock.assert_called_once_with(
        markdown_file_mock,
        pathlib.Path('./_site/here/there/somewhere.html'),
        {'title': 'Tiny Dogs', 'template': 'root.html'},
    )


def test_markdown_file_object_write_os_error(monkeypatch) -> None:
    """`MarkdownFileObject.write` raises a generic `FileObjectException` when there is a
    filesystem error.
    """
    path_mock = mock.Mock(spec=pathlib.Path())
    path_mock.name = './somewhere.md'
    settings_mock = settings.Settings(path_mock)

    markdown_file_object = files.MarkdownFileObject(path_mock, settings_mock)

    monkeypatch.setattr(pathlib.Path, 'mkdir', mock.Mock(side_effect=OSError('crikey')))
    monkeypatch.setattr(
        files.FileObject, 'target_dir', pathlib.Path('./_site/here/there')
    )

    with pytest.raises(files.FileObjectException) as exc_info:
        markdown_file_object.write()

    assert 'crikey' in str(exc_info.value)


def test_read_toml_header() -> None:
    """TODO"""

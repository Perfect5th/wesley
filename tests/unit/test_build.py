"""Unit tests for the wesley site-building logic.

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
import socket
import tempfile
from unittest import mock

from wesley import build, files, settings


def test_build_site(monkeypatch) -> None:
    """`build_site` results in a tree of HTML files mirroring the Markdown files in
    'site'.
    """
    mock_settings = mock.Mock(spec=settings.Settings, source='site', target='_site')
    is_dir_mock = mock.Mock(spec=pathlib.Path.is_dir, return_value=True)
    walk_dir_mock = mock.Mock(
        spec=build._walk_dir,
        return_value=[pathlib.Path('index.md'), pathlib.Path('meow.md')],
    )
    file_object_mock = mock.Mock(spec=files.FileObject)
    from_path_mock = mock.Mock(
        spec=files.FileObject.from_path, return_value=file_object_mock
    )

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)
    monkeypatch.setattr(build, '_walk_dir', walk_dir_mock)
    monkeypatch.setattr(build.FileObject, 'from_path', from_path_mock)

    assert not build.build_site(mock_settings)

    assert is_dir_mock.call_count == 2
    walk_dir_mock.assert_called_once_with(pathlib.Path.cwd() / 'site')
    assert from_path_mock.call_count == 2
    from_path_mock.assert_any_call(pathlib.Path('meow.md'), mock_settings)
    from_path_mock.assert_any_call(pathlib.Path('index.md'), mock_settings)


def test_build_site_not_dir(monkeypatch) -> None:
    """`build_site` returns a single error if 'site' is not a directory."""
    mock_settings = mock.Mock(spec=settings.Settings, source='site', target='_site')
    is_dir_mock = mock.Mock(spec=pathlib.Path.is_dir, return_value=False)

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)

    errors = build.build_site(mock_settings)

    is_dir_mock.assert_called_once()
    assert len(errors) == 1
    assert 'is not a directory' in errors[0]


def test_build_site_file_exists(monkeypatch) -> None:
    """`build_site` returns a single error is 'site' is an existing file."""
    mock_settings = mock.Mock(spec=settings.Settings, source='site', target='_site')
    is_dir_mock = mock.Mock(spec=pathlib.Path.is_dir, return_value=True)
    mkdir_mock = mock.Mock(pathlib.Path().mkdir, side_effect=FileExistsError())

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)
    monkeypatch.setattr(pathlib.Path, 'mkdir', mkdir_mock)

    errors = build.build_site(mock_settings)

    is_dir_mock.assert_called_once()
    mkdir_mock.assert_called_once_with(exist_ok=True)
    assert len(errors) == 1
    assert 'exists and is not a directory' in errors[0]


def test_build_site_file_object_exceptions(monkeypatch) -> None:
    """`build_site` returns as many errors as there are `FileObjectException`s."""
    mock_settings = mock.Mock(spec=settings.Settings, source='site', target='_site')
    is_dir_mock = mock.Mock(spec=pathlib.Path.is_dir, return_value=True)
    walk_dir_mock = mock.Mock(
        spec=build._walk_dir,
        return_value=[
            mock.Mock(spec=pathlib.Path),
            mock.Mock(spec=pathlib.Path),
            mock.Mock(spec=pathlib.Path),
        ],
    )
    file_object_mock = mock.Mock(spec=files.FileObject)
    file_object_mock.from_path.side_effect = [
        files.FileObjectException("he's under the comforter"),
        mock.Mock(spec=files.FileObject),
        files.FileObjectException('chewing on plastic'),
    ]

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)
    monkeypatch.setattr(build, '_walk_dir', walk_dir_mock)
    monkeypatch.setattr(build, 'FileObject', file_object_mock)

    errors = build.build_site(mock_settings)

    assert len(errors) == 2
    assert "he's under the comforter" == errors[0]
    assert 'chewing on plastic' == errors[1]


def test_walk_dir() -> None:
    """`_walk_dir` walks a directory tree, yielding each non-directory path."""
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir_path = pathlib.Path(tempdir)

        subdir_1 = tempdir_path / 'subdir_1'
        subdir_2 = tempdir_path / 'subdir_2'
        subfile_1 = tempdir_path / 'pokey.txt'

        subfile_1.write_text('he meows late at night\n')
        subdir_1.mkdir()
        subdir_2.mkdir()

        subfile_2 = subdir_1 / 'grubber.txt'
        subfile_2.write_text('she purrs in the mornings\n')

        subsubdir_1 = subdir_1 / 'sticky'
        subsubdir_1.mkdir()
        subsubfile_1 = subsubdir_1 / 'kneading.txt'
        subsubfile_1.write_text('a purrfect gentleman\nr')

        # Create a socket so we have a non-dir, non-normal-file to test
        sock = socket.socket(socket.AF_UNIX)
        sock.bind(str(subsubdir_1 / 'kittysocket'))

        walked = list(build._walk_dir(tempdir_path))

        assert len(walked) == 3

        assert subfile_1 in walked
        assert subfile_2 in walked
        assert subsubfile_1 in walked

        assert subdir_1 not in walked
        assert subdir_2 not in walked
        assert subsubdir_1 not in walked

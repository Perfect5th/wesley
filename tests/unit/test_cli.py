"""Unit tests for `wesley.cli`.

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
import argparse
import pathlib
import sys
import tarfile
from unittest import mock

import pytest

from wesley import SOURCE_DIR, VERSION, WESLEY, build, cli, settings


def test_build(capsys, monkeypatch) -> None:
    """When called, `build` produces calls `build_site`."""
    settings_mock = mock.Mock(spec=settings.Settings, errors=[])
    settings_class_mock = mock.Mock(spec=type, return_value=settings_mock)
    build_site_mock = mock.Mock(spec=build.build_site, return_value=[])

    monkeypatch.setattr(cli, 'Settings', settings_class_mock)
    monkeypatch.setattr(cli, 'build_site', build_site_mock)

    assert cli.build(argparse.Namespace()) == 0

    settings_class_mock.assert_called_once_with(pathlib.Path.cwd() / 'wesley.toml')
    build_site_mock.assert_called_once_with(settings_mock)

    outerr = capsys.readouterr()
    assert 'Building wesley project' in outerr.out
    assert WESLEY in outerr.out
    assert not outerr.err


def test_build_settings_errors(capsys, monkeypatch) -> None:
    """When called with invalid settings, `build` prints an error message."""
    settings_mock = mock.Mock(spec=settings.Settings, errors=['wesley threw up'])
    settings_class_mock = mock.Mock(spec=type, return_value=settings_mock)
    build_site_mock = mock.Mock(spec=build.build_site, return_value=[])

    monkeypatch.setattr(cli, 'Settings', settings_class_mock)
    monkeypatch.setattr(cli, 'build_site', build_site_mock)

    assert cli.build(argparse.Namespace()) == 1

    outerr = capsys.readouterr()
    assert not outerr.out
    assert 'wesley settings invalid' in outerr.err
    assert '  - wesley threw up' in outerr.err


def test_build_build_errors(capsys, monkeypatch) -> None:
    """When build errors occur, `build` prints an error message."""
    settings_mock = mock.Mock(spec=settings.Settings, errors=[])
    settings_class_mock = mock.Mock(spec=type, return_value=settings_mock)
    build_site_mock = mock.Mock(spec=build.build_site, return_value=['wesley threw up'])

    monkeypatch.setattr(cli, 'Settings', settings_class_mock)
    monkeypatch.setattr(cli, 'build_site', build_site_mock)

    assert cli.build(argparse.Namespace()) == 1

    outerr = capsys.readouterr()
    assert 'Building wesley' in outerr.out
    assert WESLEY not in outerr.out
    assert 'wesley settings invalid' not in outerr.err
    assert '  - wesley threw up' in outerr.err


@pytest.mark.parametrize(
    'arg_directory,target_directory,expected_output',
    [
        (None, pathlib.Path.cwd(), 'Initializing wesley project'),
        (
            '/supper/time',
            pathlib.Path('/supper/time'),
            'Initializing wesley project in /supper/time',
        ),
    ],
)
def test_init_success(
    arg_directory, target_directory, expected_output, capsys, monkeypatch
) -> None:
    """When called with no specified directory, `init` initializes a wesley project at
    that path.
    """
    is_dir_mock = mock.Mock(return_value=True)
    glob_mock = mock.Mock(return_value=[])
    init_directory_mock = mock.Mock()

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)
    monkeypatch.setattr(pathlib.Path, 'glob', glob_mock)
    monkeypatch.setattr(cli, 'init_directory', init_directory_mock)

    assert cli.init(argparse.Namespace(directory=arg_directory)) == 0

    is_dir_mock.assert_called_once()
    glob_mock.assert_called_once()
    init_directory_mock.assert_called_once_with(target_directory)

    out = capsys.readouterr().out
    assert expected_output in out
    assert WESLEY in out


def test_init_not_dir(capsys, monkeypatch) -> None:
    """When called with a non-directory path, `init` prints an error and returns 1."""
    is_dir_mock = mock.Mock(return_value=False)

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)

    assert cli.init(argparse.Namespace(directory=None)) == 1

    is_dir_mock.assert_called_once()

    outerr = capsys.readouterr()
    assert 'is not a directory' in outerr.err
    assert WESLEY not in outerr.out


def test_init_not_empty(capsys, monkeypatch) -> None:
    """When called with a non-empty directory path, `init` prints an error and returns
    1.
    """
    is_dir_mock = mock.Mock(return_value=True)
    glob_mock = mock.Mock(return_value=['yusss'])

    monkeypatch.setattr(pathlib.Path, 'is_dir', is_dir_mock)
    monkeypatch.setattr(pathlib.Path, 'glob', glob_mock)

    assert cli.init(argparse.Namespace(directory=None)) == 1

    is_dir_mock.assert_called_once()

    outerr = capsys.readouterr()
    assert 'is not empty' in outerr.err
    assert WESLEY not in outerr.out


def test_init_directory(monkeypatch) -> None:
    """`init_directory` untars the project tarball in the provided directory."""
    tarfile_mock = mock.Mock(spec_set=tarfile.TarFile)
    open_mock = mock.Mock(return_value=tarfile_mock)
    path = pathlib.Path('/direct/eye/contact')

    monkeypatch.setattr(tarfile, 'open', open_mock)

    cli.init_directory(path)

    open_mock.assert_called_once_with(
        SOURCE_DIR / 'templates' / 'project.tar.gz', 'r:gz'
    )
    tarfile_mock.extractall.assert_called_once_with(path)


@pytest.mark.parametrize('version_arg', ['-v', '--version'])
def test_wesley_version(version_arg, capsys, monkeypatch) -> None:
    """when called with '-v' or '--version', `wesley` prints his version number and then
    exits.
    """
    monkeypatch.setattr(sys, 'argv', ['wesley', version_arg])

    with pytest.raises(SystemExit):
        cli.wesley()

    assert VERSION in capsys.readouterr().out


@pytest.mark.parametrize(
    'directory_args', [('--directory', '/my/meowy/boy'), ('-d', '/my/hungry/lad')]
)
def test_wesley_init(directory_args, capsys, monkeypatch) -> None:
    """When called with 'init', `wesley` calls `init` on the given directory and prints
    an appropriate message.
    """
    sys_exit_mock = mock.Mock()
    init_mock = mock.Mock(return_value=0)

    monkeypatch.setattr(sys, 'argv', ['wesley', 'init'])
    monkeypatch.setattr(sys, 'exit', sys_exit_mock)
    monkeypatch.setattr(cli, 'init', init_mock)

    cli.wesley()

    sys_exit_mock.assert_called_once_with(0)
    init_mock.assert_called_once_with(
        argparse.Namespace(directory=None, func=init_mock)
    )

    monkeypatch.setattr(sys, 'argv', ['wesley', 'init', *directory_args])
    sys_exit_mock.reset_mock()
    init_mock.reset_mock()

    cli.wesley()

    sys_exit_mock.assert_called_once_with(0)
    init_mock.assert_called_once_with(
        argparse.Namespace(directory=directory_args[1], func=init_mock)
    )

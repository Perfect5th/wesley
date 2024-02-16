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
import sys
import tarfile
from unittest import mock

import pytest

from wesley import SOURCE_DIR, VERSION, WESLEY, cli


def test_init(capsys, monkeypatch) -> None:
    """When called with a directory path, `init` initializes a wesley project at that
    path.
    """
    tarfile_open_mock = mock.Mock()

    monkeypatch.setattr(tarfile, 'open', tarfile_open_mock)

    cli.init(argparse.Namespace(directory=None))

    tarfile_open_mock.assert_called_once_with(
        SOURCE_DIR / 'templates' / 'project.tar.gz', 'r:gz'
    )

    out = capsys.readouterr().out
    assert 'Initializing wesley project' in out
    assert WESLEY in out


def test_wesley_version(capsys, monkeypatch) -> None:
    """when called with '-v' or '--version', `wesley` prints his version number and then
    exits.
    """
    monkeypatch.setattr(sys, 'argv', ['wesley', '-v'])

    with pytest.raises(SystemExit):
        cli.wesley()

    assert VERSION in capsys.readouterr().out

    monkeypatch.setattr(sys, 'argv', ['wesley', '--version'])

    with pytest.raises(SystemExit):
        cli.wesley()

    assert VERSION in capsys.readouterr().out


def test_wesley_init(capsys, monkeypatch) -> None:
    """When called with 'init', `wesley` calls `init` on the given directory and prints
    an appropriate message.
    """
    init_mock = mock.Mock()

    monkeypatch.setattr(sys, 'argv', ['wesley', 'init'])
    monkeypatch.setattr(cli, 'init', init_mock)

    cli.wesley()

    init_mock.assert_called_once_with(
        argparse.Namespace(directory=None, func=init_mock)
    )

    monkeypatch.setattr(sys, 'argv', ['wesley', 'init', '--directory', '/my/meowy/boy'])
    init_mock.reset_mock()

    cli.wesley()

    init_mock.assert_called_once_with(
        argparse.Namespace(directory='/my/meowy/boy', func=init_mock)
    )

    monkeypatch.setattr(sys, 'argv', ['wesley', 'init', '-d', '/my/hungry/lad'])
    init_mock.reset_mock()

    cli.wesley()

    init_mock.assert_called_once_with(
        argparse.Namespace(directory='/my/hungry/lad', func=init_mock)
    )

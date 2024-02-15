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
import sys

import pytest

from wesley import VERSION, cli


def test_wesley_version(capsys, monkeypatch) -> None:
    """when called with '-v' or '--version', `wesley` prints his version number and then
    exits.
    """
    monkeypatch.setattr(sys, 'argv', ['wesley', '-v'])

    with pytest.raises(SystemExit):
        cli.wesley()

    assert VERSION in capsys.readouterr().out

"""Integration tests for wesley.

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
import subprocess
import sys
import tempfile
from typing import Any

from wesley import VERSION

SOURCE_DIR = pathlib.Path(__file__).parent.parent


def run_wesley(*cli_args: str, **run_kwargs: Any) -> subprocess.CompletedProcess:
    """Executes `wesley` in a subprocess, passing it additional `cli_args`. `run_kwargs`
    are passed to `subprocess.run`.
    """
    return subprocess.run(
        [sys.executable, '-m', 'wesley', *cli_args],
        capture_output=True,
        check=True,
        text=True,
        env={'PYTHONPATH': SOURCE_DIR},
        **run_kwargs,
    )


def test_init() -> None:
    """Executing `wesley init` results in a reasonable directory layout with which to
    start a static site.

    We do this in a temporary directory for ease of cleanup.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        stdout = run_wesley('init', cwd=tempdir).stdout

        assert stdout
        assert '\N{CAT}\N{ZWJ}\N{BLACK LARGE SQUARE}' in stdout

        tempdir_path = pathlib.Path(tempdir)
        contents = list(tempdir_path.glob('*'))

        assert 'site' in contents
        assert (tempdir_path / 'site').is_dir()


def test_version() -> None:
    """Executing `wesley -v` or `wesley --version` outputs the current version of the
    application.
    """
    stdout = run_wesley('-v').stdout

    assert stdout
    assert VERSION in stdout
    assert '\N{CAT}\N{ZWJ}\N{BLACK LARGE SQUARE}' in stdout

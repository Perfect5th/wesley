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
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from typing import Any

import pytest

from wesley import SOURCE_DIR, VERSION, WESLEY

PROJECT_DIR = SOURCE_DIR.parent


def run_wesley(*cli_args: str, **run_kwargs: Any) -> subprocess.CompletedProcess:
    """Executes `wesley` in a subprocess, passing it additional `cli_args`. `run_kwargs`
    are passed to `subprocess.run`.
    """
    return subprocess.run(
        [sys.executable, '-m', 'wesley', *cli_args],
        capture_output=True,
        check=True,
        text=True,
        env={'PYTHONPATH': PROJECT_DIR},
        **run_kwargs,
    )


def test_build() -> None:
    """Executing `wesley build` results in a tree of HTML files mirroring the files in
    the 'site' directory.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir_path = pathlib.Path(tempdir)
        sample_tarfile = tarfile.open(
            PROJECT_DIR / 'tests' / 'fixtures' / 'sample.tar.gz'
        )
        sample_tarfile.extractall(tempdir_path / 'site')

        stdout = run_wesley('build', cwd=tempdir).stdout

        assert WESLEY in stdout
        assert 'Building' in stdout
        assert "He's built" in stdout

        assert (tempdir_path / '_site').is_dir()
        assert (tempdir_path / '_site' / 'index.html').is_file()


def test_init() -> None:
    """Executing `wesley init` results in a reasonable directory layout with which to
    start a static site.

    We do this in a temporary directory for ease of cleanup.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        stdout = run_wesley('init', cwd=tempdir).stdout

        assert stdout
        assert WESLEY in stdout

        tempdir_path = pathlib.Path(tempdir)

        assert (tempdir_path / 'site').is_dir()
        assert (tempdir_path / 'site' / 'index.md').is_file()


def test_init_refuses_non_empty() -> None:
    """Executing `wesley init` on a non-empty directory results in an error."""
    with tempfile.TemporaryDirectory() as tempdir:
        shutil.copy(__file__, tempdir)

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            run_wesley('init', cwd=tempdir)

    assert 'is not empty' in exc_info.value.stderr


def test_version() -> None:
    """Executing `wesley -v` or `wesley --version` outputs the current version of the
    application.

    It should also match what's in pyproject.toml.
    """
    with open(PROJECT_DIR / 'pyproject.toml', 'rb') as pyproject_toml_fp:
        pyproject_version = tomllib.load(pyproject_toml_fp)['tool']['poetry']['version']

    assert VERSION == pyproject_version

    stdout = run_wesley('-v').stdout

    assert WESLEY in stdout
    assert stdout
    assert VERSION in stdout

    stdout = run_wesley('--version').stdout

    assert WESLEY in stdout
    assert stdout
    assert VERSION in stdout

"""Integration tests for wesley."""

import pathlib
import subprocess
import sys
import tempfile

SOURCE_DIR = pathlib.Path(__file__).parent.parent


def test_init() -> None:
    """Executing `wesley init` results in a reasonable directory layout with which to
    start a static site.

    We do this in a temporary directory for ease of cleanup.
    """
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            completed_process = subprocess.run(
                [sys.executable, '-m', 'wesley', 'init'],
                capture_output=True,
                cwd=tempdir,
                check=True,
                text=True,
                env={'PYTHONPATH': SOURCE_DIR},
            )
        except subprocess.CalledProcessError as cpe:
            raise Exception(f"Error in init call: {cpe.stderr}")

    assert len(completed_process.stdout)
    assert '\N{CAT}\N{ZWJ}\N{BLACK LARGE SQUARE}' in completed_process.stdout

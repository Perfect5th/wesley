"""The wesley CLI.

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

from . import VERSION, WESLEY


def wesley():
    """The main entry-point for wesley. Parses CLI parameters and triages accordingly.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version', version=f'wesley {VERSION} {WESLEY}')
    parser.parse_args(sys.argv)


if __name__ == '__main__':
    wesley()

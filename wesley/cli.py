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
import pathlib
import sys
import tarfile

from . import SOURCE_DIR, VERSION, WESLEY


def build(_: argparse.Namespace) -> int:
    """Builds a wesley project, turning Markdown files in 'site' into HTML files in
    '_site'.
    """
    print('Building wesley project...')

    print(f"{WESLEY} He's built!")

    return 0


def init(args: argparse.Namespace) -> int:
    """Initializes a wesley project in `directory` by extracting the template tarball."""
    if args.directory:
        directory_path = pathlib.Path(args.directory)
    else:
        directory_path = pathlib.Path.cwd()

    if not directory_path.is_dir():
        print(f'{directory_path} is not a directory', file=sys.stderr)
        return 1

    if list(directory_path.glob('*')):
        print(f'{directory_path} is not empty', file=sys.stderr)
        return 1

    if directory_path != pathlib.Path.cwd():
        print(f'Initializing wesley project in {directory_path}')
    else:
        print('Initializing wesley project')

    init_directory(directory_path)

    print(f"{WESLEY} He's ready!")

    return 0


def init_directory(directory: pathlib.Path) -> None:
    """Extracts the template tarball into `directory`."""
    project_tarfile = tarfile.open(SOURCE_DIR / 'templates' / 'project.tar.gz', 'r:gz')
    project_tarfile.extractall(directory)


def wesley():
    """The main entry-point for wesley. Parses CLI parameters and triages accordingly."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version', '-v', action='version', version=f'wesley {VERSION} {WESLEY}'
    )

    subparsers = parser.add_subparsers()

    parser_build = subparsers.add_parser('build')
    parser_build.set_defaults(func=build)

    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init)
    parser_init.add_argument('--directory', '-d')

    args = parser.parse_args(sys.argv[1:])
    sys.exit(args.func(args))


if __name__ == '__main__':  # pragma: no cover
    wesley()

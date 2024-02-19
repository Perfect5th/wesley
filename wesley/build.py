"""The wesley site-building logic.

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
from collections.abc import Iterator

from .files import FileObject
from .settings import Settings


def build_site(settings: Settings) -> list[str]:
    """Builds a wesley project, turning Markdown files in 'site" into HTML files in
    '_site'

    :param settings: The wesley site settings.
    :returns: Any accrued error messages.
    """
    site_path = pathlib.Path.cwd() / 'site'

    if not site_path.is_dir():
        return ['./site is not a directory']

    output_path = pathlib.Path.cwd() / '_site'

    try:
        output_path.mkdir(exist_ok=True)
    except FileExistsError:
        return ['./_site exists and is not a directory']

    for path in _walk_dir(site_path):
        FileObject.from_path(path).write()

    return []


def _walk_dir(dir: pathlib.Path) -> Iterator[pathlib.Path]:
    """Generator that walks the file tree at `dir`, yielding each non-dir path.
    We assume that `dir` is a directory.
    """
    stack = [dir]

    while stack:
        current_dir = stack.pop()

        for child in current_dir.iterdir():
            if child.is_dir():
                stack.append(child)
            elif child.is_file():
                yield child

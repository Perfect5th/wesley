"""The wesley file-handling logic.

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
import abc
import pathlib
from functools import cached_property

from .settings import Settings


class FileObject(abc.ABC):
    """Abstract class representing a file to wesley.

    :param path: The path at which this file is present.
    :param settings: The global wesley settings.
    """

    def __init__(self, path: pathlib.Path, settings: Settings) -> None:
        self.path = path
        self.settings = settings

    @cached_property
    def target_dir(self) -> pathlib.Path:
        """The target directory where this `FileObject` will be written, as determined
        by `path` and `settings.target`.
        """
        parts = [
            part if part != self.settings.source else self.settings.target
            for part in self.path.parts
        ]

        return pathlib.Path(*parts).parent

    @abc.abstractmethod
    def write(self) -> None:
        """Writes this `FileObject` to the appropriate output file type."""

    @staticmethod
    def from_path(path: pathlib.Path, settings: Settings) -> 'FileObject':
        """Produces a `FileObject` subclass instance based on the filename
        (not detected MIME) of the file at `path`.
        """
        if path.suffix == '.md':
            return MarkdownFileObject(path, settings)

        return GenericFileObject(path, settings)


class FileObjectException(Exception):
    """An exception raised by a `FileObject` subclass."""


class GenericFileObject(FileObject):
    """Class representing a file with a type we are not concerned about."""

    def write(self) -> None:
        """Writes this `GenericFileObject` to another location, in the target
        directory.
        """
        target_path = self.target_dir / self.path.name

        target_path.mkdir(exist_ok=True)
        target_path.write_bytes(self.path.read_bytes())


class MarkdownFileObject(FileObject):
    """Class representing a wesley-frontmattered Markdown file."""

    def write(self) -> None:
        """Writes this `MarkdownFileObject` to an HTML file, rendered in the selected
        template.
        TODO: stub
        """

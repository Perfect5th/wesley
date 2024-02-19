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


class FileObject(abc.ABC):
    """Abstract class representing a file to wesley."""

    @abc.abstractmethod
    def write(self) -> None:
        """Writes this `FileObject` to the appropriate output file type."""

    @staticmethod
    def from_path(path: pathlib.Path) -> 'FileObject':
        """TODO: stub"""
        return MarkdownFileObject()


class MarkdownFileObject(FileObject):
    """Class representing a wesley-frontmattered Markdown file."""

    def write(self) -> None:
        """Writes this `MarkdownFileObject` to an HTML file, rendered in the selected
        template.
        TODO: stub
        """

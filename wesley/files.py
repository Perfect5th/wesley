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
import io
import pathlib
import re
from functools import cached_property
from typing import Mapping

import jinja2

from .settings import Settings, jinja_env


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

        :raises FileObjectException: if any exceptions are raised during directory or
            file read/write.
        """
        target_path = self.target_dir / self.path.name

        try:
            target_path.mkdir(exist_ok=True)
            target_path.write_bytes(self.path.read_bytes())
        except OSError as e:
            raise FileObjectException(e)


class MarkdownFileObject(FileObject):
    """Class representing a wesley-frontmattered Markdown file."""

    def write(self) -> None:
        """Writes this `MarkdownFileObject` to an HTML file, rendered in the selected
        template.

        :raises FileObjectException: if any exceptions are raised during directory or
            file read/write.
        """
        target_path = self.target_dir / re.sub(r'\.md$', '.html', self.path.name)

        try:
            target_path.mkdir(exist_ok=True)

            with self.path.open() as markdown_file:
                toml_header = self.read_toml_header(markdown_file)

                if 'template' not in toml_header:
                    raise MissingFrontMatterException(self.path, 'template')

                self.render(markdown_file, target_path, toml_header)
        except OSError as e:
            raise FileObjectException(e)

    def read_toml_header(self, markdown_file: io.TextIOWrapper) -> dict[str, str]:
        """Reads the TOML-formatted header of `markdown_file`, parsing it to a
        dictionary.

        TODO: stub
        """
        return {}

    def render(
        self,
        markdown_file: io.TextIOWrapper,
        target_path: pathlib.Path,
        toml_header: Mapping[str, str],
    ) -> None:
        """TODO: stub"""


class MissingFrontMatterException(FileObjectException):
    """A `FileObjectException` raised when a `MarkdownFileObject`'s TOML front-matter is
    missing a required field.
    """

    def __init__(self, file_object_path: pathlib.Path, missing_key: str) -> None:
        super().__init__(
            f"Error rendering {file_object_path}: '{missing_key}' missing from TOML"
            ' front-matter.'
        )


class TemplateNotFoundException(FileObjectException):
    """A `FileObjectException` raised when a `MarkdownFileObject`'s template cannot be
    found.
    """

    def __init__(self, file_object_path: pathlib.Path, template_name: str) -> None:
        super().__init__(
            f"Error rendering {file_object_path}: template '{template_name}' not found."
        )

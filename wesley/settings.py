"""The wesley settings module.

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


class Settings:
    """Represents the settings used to generate a wesley project.

    :param toml_path: Path to the TOML-formatted settings file, used for initialization.
    """

    def __init__(self, toml_path: pathlib.Path) -> None:
        """TODO: this is a stub"""
        self.source = 'site'
        self.target = '_site'

        self.errors: list[str] = []

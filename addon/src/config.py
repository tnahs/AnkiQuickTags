from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import aqt

from .helpers import ConfigError, Defaults, Key
from .tag import Tag


class Config:
    """A class used to store the add-on's configuration.

    During testing, the `data` argument can be supplied to bypass loading the
    configuration from disk.

    The data structure is as follows:

    {
        "quick-tags": [
            {
                "name": "QuickTag-01",
                "shortcut": "Ctrl+Alt+T"
            },
            ...
        ],
        "other-tags": {
            "visible": true,
            "limit": 10
        }
    }
    """

    _data: dict[str, Any] = {}
    _quick_tags: list[Tag] = []
    _other_tags: list[Tag] = []

    def __init__(self, data: dict | None = None) -> None:
        self.reload(data=data)

    def reload(self, data: dict | None = None) -> None:
        """Re-load and re-build the add-on's configuration."""

        self._data = self._load() if data is None else data
        self._validate()
        self._build_quick_tags()
        self._build_other_tags()

    @property
    def quick_tags(self) -> list[Tag]:
        """Returns a list of the quick-tags."""

        return self._quick_tags

    @property
    def other_tags(self) -> list[Tag]:
        """Returns a list of the other-tags."""

        return self._other_tags

    @property
    def other_tags_are_visible(self) -> bool:
        """Returns a bool for whether or not to show other-tags."""

        return self._other_tags_raw_config.get(
            Key.VISIBLE, Defaults.OTHER_TAGS_ARE_VISIBLE
        )

    @property
    def other_tags_limit(self) -> int:
        """Returns a integer indicating how many other-tags to show."""

        return self._other_tags_raw_config.get(Key.LIMIT, Defaults.OTHER_TAGS_LIMIT)

    def _load(self) -> dict:
        """Loads the add-on's configuration from disk."""

        try:
            with open(Defaults.TAGS_JSON) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Missing {Key.TAGS_JSON} in {Defaults.USER_FILES}.")
        except json.JSONDecodeError:
            raise ConfigError(f"Cannot read {Key.TAGS_JSON} in {Defaults.USER_FILES}.")

        return data

    def _validate(self):
        """Validates the add-on's configuration."""

        for (name, _) in self._iter_raw_config():
            if not name:
                raise ConfigError(f"All tags require a '{Key.NAME}'.")

        if not isinstance(self.other_tags_are_visible, bool):
            raise ConfigError(
                f"Invalid type for '{Key.OTHER_TAGS}:{Key.VISIBLE}'. Expected bool, "
                f"found {type(self.other_tags_are_visible)}'."
            )

        if not isinstance(self.other_tags_limit, int):
            raise ConfigError(
                f"Invalid type for '{Key.OTHER_TAGS}:{Key.LIMIT}'. Expected int found "
                f"{type(self.other_tags_limit)}'."
            )

    def _build_quick_tags(self) -> None:
        """Builds a list of the quick-tags."""

        self._quick_tags *= 0

        for (name, shortcut) in self._iter_raw_config():

            self._quick_tags.append(
                Tag(
                    name=name,
                    shortcut=shortcut,
                )
            )

            self._quick_tags.sort(key=lambda tag: tag.name)

    def _build_other_tags(self) -> None:
        """Builds a list of the other-tags i.e. tags that do not appear in the quick-
        tags list."""

        if aqt.mw is None or aqt.mw.col is None:
            return

        self._other_tags *= 0

        quick_tags = [tag.name for tag in self.quick_tags]

        tags = aqt.mw.col.tags.all()
        tags = sorted([tag for tag in tags if tag not in quick_tags])
        tags = tags[: self.other_tags_limit + 1]

        for name in tags:
            self._other_tags.append(
                Tag(
                    name=name,
                    shortcut="",  # Other tags don't have shortcuts.
                )
            )

        self._other_tags.sort(key=lambda tag: tag.name)

    @property
    def _other_tags_raw_config(self) -> dict:
        """Returns the raw configuration for the `other-tags` entry."""

        return self._data.get(Key.OTHER_TAGS, {})

    def _iter_raw_config(self) -> Iterator[tuple[str, str]]:
        """Iterates through the raw config data and returns a tuple for each quick-tag
        containing its name and shortcut."""

        for tag in self._data.get(Key.TAGS, []):

            name = tag.get(Key.NAME, "")
            shortcut = tag.get(Key.SHORTCUT, "")

            if not name and not shortcut:
                continue

            yield (name, shortcut)

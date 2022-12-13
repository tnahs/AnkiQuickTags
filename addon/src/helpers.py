from __future__ import annotations

import os
import pathlib

import aqt
import aqt.utils
from anki.notes import Note


def is_development_mode() -> bool:
    """Returns a bool for whether or not the the add-on is being developed."""

    return "ANKI_ADDON_DEVELOPMENT" in os.environ


def show_info(message: str) -> None:
    """Shows the user a message related to this add-on."""

    aqt.utils.showInfo(f"{Defaults.NAME}: {message}")


def get_reviewing_note() -> Note | None:
    """Returns the current note being reviewed."""

    if aqt.mw is None:
        return

    card = aqt.mw.reviewer.card

    if card is None:
        return

    return card.note()


class ConfigError(Exception):
    """The exception raised when the addon's configuration is missing, has JSON syntax
    errors, is missing keys, or has other general configuration errors."""

    pass


class Key:
    """A class defining re-usable strings."""

    DECK_BROWSER = "deckBrowser"
    LIMIT = "limit"
    NAME = "name"
    OTHER_TAGS = "other-tags"
    REVIEW = "review"
    SHORTCUT = "shortcut"
    TAGS = "tags"
    TAGS_JSON = "tags.json"
    USER_FILES = "user_files" if not is_development_mode() else "user_files_dev"
    VISIBLE = "visible"


class Defaults:
    """A class defining all the add-on's default values."""

    NAME = "AnkiQuickTags"

    # [path-to-addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [path-to-addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [path-to-addon]/user_files/tags.json
    TAGS_JSON = USER_FILES / Key.TAGS_JSON

    OTHER_TAGS_ARE_VISIBLE = True
    OTHER_TAGS_LIMIT = 10

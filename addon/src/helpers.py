import os
import pathlib


class ConfigError(Exception):
    pass


class Key:
    LIMIT = "limit"
    NAME = "name"
    OTHER_TAGS = "other-tags"
    QUICK_TAGS = "quick-tags"
    REVIEW = "review"
    SHORTCUT = "shortcut"
    TAGS_JSON = "tags.json"
    USER_FILES = (
        "user_files"
        if "ANKI_ADDON_DEVELOPMENT" not in os.environ
        else "user_files__dev"
    )
    VISIBLE = "visible"


class Defaults:
    NAME = "AnkiQuickTags"

    # [/absolute/path/to/addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [/absolute/path/to/addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [/absolute/path/to/addon]/user_files/tags.json
    TAGS_JSON = USER_FILES / Key.TAGS_JSON

    OTHER_TAGS_VISIBLE = True
    OTHER_TAGS_LIMIT = 10

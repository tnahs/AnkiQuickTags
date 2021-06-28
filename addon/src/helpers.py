import os
import pathlib


class Key:
    CONFIG_JSON = (
        "config.json"
        if not os.environ.get("ANKI_ADDON_DEV", False)
        else "config_dev.json"
    )
    QUICK_TAGS = "quick-tags"
    NAME = "name"
    SHORTCUT = "shortcut"
    OTHER_TAGS = "other-tags"
    VISIBLE = "visible"
    LIMIT = "limit"
    REVIEW = "review"


class Defaults:
    NAME = "AnkiQuickTags"

    # [/absolute/path/to/addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [/absolute/path/to/addon]/config.json
    CONFIG_JSON = ADDON_ROOT / Key.CONFIG_JSON

    OTHER_TAGS_VISIBLE = True
    OTHER_TAGS_LIMIT = 10


class ConfigError(Exception):
    pass

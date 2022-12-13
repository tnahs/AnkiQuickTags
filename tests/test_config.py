import pytest

from addon.src.config import Config
from addon.src.helpers import ConfigError, Key
from addon.src.tag import Tag


def test__valid_config(tags: list[Tag]) -> None:
    data = {
        Key.TAGS: [
            {
                Key.NAME: "Tag01",
                Key.SHORTCUT: "Ctrl+1",
            },
            {
                Key.NAME: "Tag02",
                Key.SHORTCUT: "Ctrl+2",
            },
            {
                Key.NAME: "Tag03",
                Key.SHORTCUT: "Ctrl+3",
            },
        ],
        Key.OTHER_TAGS: {
            Key.VISIBLE: True,
            Key.LIMIT: 10,
        },
    }

    config = Config(data=data)

    assert config.quick_tags == tags


def test__missing_name() -> None:
    data = {
        Key.TAGS: [
            {
                # MISSING NAME
                Key.SHORTCUT: "Ctrl+1",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__blank_name() -> None:
    data = {
        Key.TAGS: [
            {
                Key.NAME: "",
                Key.SHORTCUT: "Ctrl+1",
            },
        ]
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__invalid_type_for_visible() -> None:
    data = {
        Key.OTHER_TAGS: {
            Key.VISIBLE: "true",
        }
    }

    with pytest.raises(ConfigError):
        Config(data=data)


def test__invalid_type_for_limit() -> None:
    data = {
        Key.OTHER_TAGS: {
            Key.LIMIT: "10",
        }
    }

    with pytest.raises(ConfigError):
        Config(data=data)

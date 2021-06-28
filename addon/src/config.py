import json
from typing import Iterator, Tuple

from .helpers import ConfigError, Defaults, Key


class Config:
    def load(self) -> None:

        try:
            with open(Defaults.CONFIG_JSON, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(
                f"Missing {Key.CONFIG_JSON} in {Defaults.CONFIG_JSON.parent}."
            )
        except json.JSONDecodeError:
            raise ConfigError(
                f"Cannot read {Key.CONFIG_JSON} in {Defaults.CONFIG_JSON.parent}."
            )

        self.__data = data

    @property
    def quick_tags(self) -> Iterator[Tuple[str, str]]:

        for tag in self.__data.get(Key.QUICK_TAGS, []):

            name = tag.get(Key.NAME, None)
            shortcut = tag.get(Key.SHORTCUT, None)

            if not name or not shortcut:
                continue

            yield (name, shortcut)

    @property
    def other_tags(self) -> dict:
        return self.__data.get(Key.OTHER_TAGS, {})

    @property
    def other_tags_visible(self) -> bool:
        return self.other_tags.get(Key.VISIBLE, Defaults.OTHER_TAGS_VISIBLE)

    @property
    def other_tags_limit(self) -> int:
        return self.other_tags.get(Key.LIMIT, Defaults.OTHER_TAGS_LIMIT)

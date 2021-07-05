import json
from typing import Iterator, List, Optional, Tuple

from .helpers import ConfigError, Defaults, Key
from .tag import QuickTag


class Config:

    __data = {}
    __quick_tags: List[QuickTag] = []

    def __init__(self, data: Optional[dict] = None) -> None:

        self.__data = self.__load() if data is None else data
        self.__validate()
        self.__build_quick_tags()

    def __load(self) -> dict:

        try:
            with open(Defaults.TAGS_JSON, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Missing {Key.TAGS_JSON} in {Defaults.USER_FILES}.")
        except json.JSONDecodeError:
            raise ConfigError(f"Cannot read {Key.TAGS_JSON} in {Defaults.USER_FILES}.")

        return data

    def __validate(self):
        pass

    def __iter_quick_tags(self) -> Iterator[Tuple[str, str]]:

        for tag in self.__data.get(Key.QUICK_TAGS, []):

            name = tag.get(Key.NAME, None)
            shortcut = tag.get(Key.SHORTCUT, None)

            if not name or not shortcut:
                continue

            yield (name, shortcut)

    def __build_quick_tags(self) -> None:

        self.__quick_tags *= 0

        for (name, shortcut) in self.__iter_quick_tags():

            self.__quick_tags.append(
                QuickTag(
                    name=name,
                    shortcut=shortcut,
                )
            )

            self.__quick_tags.sort(key=lambda tag: tag.name)

    def reload(self) -> None:

        self.__data = self.__load()
        self.__validate()
        self.__build_quick_tags()

    @property
    def quick_tags(self) -> List[QuickTag]:
        return self.__quick_tags

    @property
    def other_tags(self) -> dict:
        return self.__data.get(Key.OTHER_TAGS, {})

    @property
    def other_tags_visible(self) -> bool:
        return self.other_tags.get(Key.VISIBLE, Defaults.OTHER_TAGS_VISIBLE)

    @property
    def other_tags_limit(self) -> int:
        return self.other_tags.get(Key.LIMIT, Defaults.OTHER_TAGS_LIMIT)

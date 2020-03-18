import functools
import json
import pathlib
from typing import Optional

import aqt
import anki

from . import errors


class AnkiQuickTags:

    name = "AnkiQuickTags"

    main_root = pathlib.Path(__file__).parent.parent
    user_root = main_root / "user_files"
    config_path = main_root / "config.json"

    def __init__(self) -> None:

        self._load_config()

    def _load_config(self) -> None:

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise errors.ConfigError("Missing `config.json`.")
        except json.JSONDecodeError:
            raise errors.ConfigError("Cannot read `config.json`.")

        self._config = config

    @property
    def _show_tags_other(self) -> bool:
        return self._config.get("show-other-tags", True)

    @property
    def _tags_other_limit(self) -> int:
        return self._config.get("other-tags-limit", 10)

    @property
    def _reviewer(self) -> aqt.reviewer.Reviewer:
        return aqt.mw.reviewer

    @property
    def _note(self) -> anki.notes.Note:
        return self._reviewer.card.note()

    @property
    def _tags_all(self) -> list:
        return sorted(aqt.mw.col.tags.all())

    @property
    def _tags_note(self) -> list:
        return sorted(self._note.tags)

    @property
    def _tags_config(self) -> list:
        return self._config.get("tags", [])

    @property
    def _tags_other(self) -> list:
        return sorted([tag for tag in self._tags_all if tag not in self._tags_config])

    def _create_menu_action(
        self, menu: aqt.qt.QMenu, tag: str, shortcut: Optional[str] = None
    ) -> aqt.qt.QAction:

        action = aqt.qt.QAction(tag, menu)
        action.setCheckable(True)
        action.setChecked(self._note.hasTag(tag))

        # TODO: Dont hide menu until clicked off... Allow the user to check
        # more than one tag at a time.
        action.toggled.connect(functools.partial(self.action__toggle_tag, tag=tag))

        if shortcut is not None:
            action.setShortcut(shortcut)

        return action

    def action__toggle_tag(self, tag: str) -> None:

        if self._note.hasTag(tag):
            self._note.delTag(tag)
            aqt.utils.tooltip(f"Removed '{tag}'")
        else:
            self._note.addTag(tag)
            aqt.utils.tooltip(f"Added '{tag}'")

        self._note.flush()

    def setup(self) -> None:
        def hook__build_context_menu(
            webview: aqt.webview.AnkiWebView, menu: aqt.qt.QMenu
        ) -> None:

            if aqt.mw.state != "review":
                return

            menu.addSeparator()

            for tag in self._tags_config:

                if not tag:
                    continue

                action = self._create_menu_action(menu=menu, tag=tag)

                menu.addAction(action)

            if self._show_tags_other:

                sub_menu = aqt.qt.QMenu("Other Tags...", menu)

                for tag in self._tags_other[: self._tags_other_limit]:

                    action = self._create_menu_action(menu=sub_menu, tag=tag)

                    sub_menu.addAction(action)

                menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(hook__build_context_menu)

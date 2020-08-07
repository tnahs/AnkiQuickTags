import functools
import json
import pathlib
from typing import Optional, List, Callable, Tuple

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

        quick_tags = config.get("quick-tags", None)

        if quick_tags is None:
            raise errors.ConfigError("Missing `quick-tags` in `config.json`.")

        for tag in quick_tags:

            tag_name = tag.get("name", None)

            if not tag_name:
                raise errors.ConfigError("All items in `quick-tags` require a `name`.")

        self._config = config

    @property
    def _show_additional_tags(self) -> bool:
        return self._config.get("additional-tags", True)

    @property
    def _additional_tags_limit(self) -> int:
        return self._config.get("additional-tags-limit", 10)

    @property
    def _reviewer(self) -> aqt.reviewer.Reviewer:
        return aqt.mw.reviewer

    @property
    def _note(self) -> anki.notes.Note:
        return self._reviewer.card.note()

    @property
    def _all_tags(self) -> list:
        return sorted(aqt.mw.col.tags.all())

    @property
    def _note_tags(self) -> list:
        return sorted(self._note.tags)

    @property
    def _quick_tags(self) -> list:
        return self._config.get("quick-tags", [])

    @property
    def _additional_tags(self) -> list:
        return sorted([tag for tag in self._all_tags if tag not in self._quick_tags])

    def _create_menu_action(self, menu: aqt.qt.QMenu, tag_name: str) -> aqt.qt.QAction:

        action = aqt.qt.QAction(tag_name, menu)
        action.setCheckable(True)
        action.setChecked(self._note.hasTag(tag_name))

        action.toggled.connect(
            functools.partial(self.action__toggle_tag, tag_name=tag_name)
        )

        return action

    def action__toggle_tag(self, tag_name: str) -> None:

        if self._note.hasTag(tag_name):
            self._note.delTag(tag_name)
            aqt.utils.tooltip(f"Removed '{tag_name}'...")
        else:
            self._note.addTag(tag_name)
            aqt.utils.tooltip(f"Added '{tag_name}'...")

        self._note.flush()

    def setup(self) -> None:
        def hook__append_context_menu(
            webview: aqt.webview.AnkiWebView, menu: aqt.qt.QMenu
        ) -> None:

            if aqt.mw.state != "review":
                return

            menu.addSeparator()

            for item in self._quick_tags:

                tag_name = item.get("name")

                action = self._create_menu_action(menu=menu, tag_name=tag_name)

                menu.addAction(action)

            if self._show_additional_tags:

                sub_menu = aqt.qt.QMenu("Additional Tags...", menu)

                for name in self._additional_tags[: self._additional_tags_limit]:

                    action = self._create_menu_action(menu=sub_menu, tag_name=name)

                    sub_menu.addAction(action)

                menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(hook__append_context_menu)

        def hook__append_shortcuts(
            state: str, shortcuts: List[Tuple[str, Callable]]
        ) -> None:

            if state != "review":
                return

            for tag in self._quick_tags:

                tag_name = tag.get("name", None)
                tag_shortcut = tag.get("shortcut", None)

                if not tag_shortcut:
                    continue

                shortcuts.append(
                    (
                        tag_shortcut,
                        functools.partial(self.action__toggle_tag, tag_name=tag_name),
                    )
                )

        aqt.gui_hooks.state_shortcuts_will_change.append(hook__append_shortcuts)

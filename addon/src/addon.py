import functools
from typing import Callable, List, Tuple

import anki
import anki.notes
import aqt
import aqt.gui_hooks
import aqt.utils
from aqt.webview import AnkiWebView
from PyQt5.QtWidgets import QAction, QMenu

from .config import Config
from .helpers import Key


class AnkiQuickTags:
    def __init__(self) -> None:
        self.__config = Config()

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def note(self) -> anki.notes.Note:
        return aqt.mw.reviewer.card.note()

    @property
    def all_tags(self) -> List[str]:
        return sorted(aqt.mw.col.tags.all())

    @property
    def note_tags(self) -> List[str]:
        return sorted(self.note.tags)

    @property
    def quick_tags(self) -> List[str]:
        return sorted([tag for (tag, _) in self.config.quick_tags])

    @property
    def other_tags(self) -> List[str]:

        other_tags = sorted(
            [tag for tag in self.all_tags if tag not in self.quick_tags]
        )

        return other_tags[: self.config.other_tags_limit]

    def action__toggle_tag(self, tag: str) -> None:

        if self.note.hasTag(tag):
            self.note.delTag(tag)
            aqt.utils.tooltip(f"Removed '{tag}'...")
        else:
            self.note.addTag(tag)
            aqt.utils.tooltip(f"Added '{tag}'...")

        self.note.flush()

    def setup(self) -> None:
        def hook__append_context_menu(
            webview: AnkiWebView, context_menu: QMenu
        ) -> None:

            if aqt.mw.state != Key.REVIEW:
                return

            self.config.load()

            context_menu.addSeparator()

            for tag in self.quick_tags:

                action = QAction(tag, context_menu)
                action.setCheckable(True)
                action.setChecked(self.note.hasTag(tag))
                action.toggled.connect(
                    functools.partial(self.action__toggle_tag, tag=tag)
                )

                context_menu.addAction(action)

            if self.config.other_tags_visible:

                sub_menu = QMenu("Other Tags...", context_menu)

                for tag in self.other_tags:

                    action = QAction(tag, sub_menu)
                    action.setCheckable(True)
                    action.setChecked(self.note.hasTag(tag))
                    action.toggled.connect(
                        functools.partial(self.action__toggle_tag, tag=tag)
                    )

                    sub_menu.addAction(action)

                context_menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(hook__append_context_menu)

        def hook__append_shortcuts(
            state: str, shortcuts: List[Tuple[str, Callable]]
        ) -> None:

            if state != Key.REVIEW:
                return

            self.config.load()

            for (tag, shortcut) in self.config.quick_tags:

                shortcuts.append(
                    (
                        shortcut,
                        functools.partial(self.action__toggle_tag, tag=tag),
                    )
                )

        aqt.gui_hooks.state_shortcuts_will_change.append(hook__append_shortcuts)

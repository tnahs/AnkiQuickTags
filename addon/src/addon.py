import functools
from typing import Callable, List, Tuple

import aqt
import aqt.gui_hooks
import aqt.utils
from anki.notes import Note
from aqt.webview import AnkiWebView
from PyQt5.QtWidgets import QAction, QMenu

from .config import Config
from .helpers import Key


class AnkiQuickTags:
    def __init__(self) -> None:
        self.__config = Config()

    def __action__toggle_tag(self, tag_name: str) -> None:

        if self.current_note.hasTag(tag_name):
            self.current_note.delTag(tag_name)
            aqt.utils.tooltip(f"Removed '{tag_name}'...")
        else:
            self.current_note.addTag(tag_name)
            aqt.utils.tooltip(f"Added '{tag_name}'...")

        self.current_note.flush()

    def setup(self) -> None:
        def __hook__append_context_menu(
            webview: AnkiWebView, context_menu: QMenu
        ) -> None:

            if aqt.mw.state != Key.REVIEW:  # type: ignore
                return

            self.config.reload()

            context_menu.addSeparator()

            for tag in self.config.quick_tags:

                action = QAction(tag.name, context_menu)
                action.setCheckable(True)
                action.setChecked(self.current_note.hasTag(tag.name))
                action.toggled.connect(
                    functools.partial(
                        self.__action__toggle_tag,
                        tag_name=tag.name,
                    )
                )

                context_menu.addAction(action)

            if self.config.other_tags_visible:

                sub_menu = QMenu("Other Tags...", context_menu)

                for tag_name in self.other_tags:

                    action = QAction(tag_name, sub_menu)
                    action.setCheckable(True)
                    action.setChecked(self.current_note.hasTag(tag_name))
                    action.toggled.connect(
                        functools.partial(
                            self.__action__toggle_tag,
                            tag_name=tag_name,
                        )
                    )

                    sub_menu.addAction(action)

                context_menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(__hook__append_context_menu)

        def __hook__append_shortcuts(
            state: str, shortcuts: List[Tuple[str, Callable]]
        ) -> None:

            if state != Key.REVIEW:
                return

            self.config.reload()

            for tag in self.config.quick_tags:

                shortcuts.append(
                    (
                        tag.shortcut,
                        functools.partial(
                            self.__action__toggle_tag,
                            tag_name=tag.name,
                        ),
                    )
                )

        aqt.gui_hooks.state_shortcuts_will_change.append(__hook__append_shortcuts)

    @property
    def config(self) -> Config:
        return self.__config

    @property
    def other_tags(self) -> List[str]:

        all_tags = aqt.mw.col.tags.all()  # type: ignore
        quick_tags = [tag.name for tag in self.config.quick_tags]
        other_tags = sorted([tag for tag in all_tags if tag not in quick_tags])

        return other_tags[: self.config.other_tags_limit]

    @property
    def current_note(self) -> Note:
        return aqt.mw.reviewer.card.note()  # type: ignore

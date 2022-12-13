from __future__ import annotations

import functools
from typing import Callable

import aqt
import aqt.gui_hooks
import aqt.utils
from anki.notes import Note
from aqt.qt.qt6 import QAction, QMenu
from aqt.webview import AnkiWebView

from .config import Config
from .helpers import Key, get_reviewing_note


class AnkiQuickTags:
    def __init__(self) -> None:
        self._config = Config()

    def setup(self) -> None:

        if aqt.mw is None:
            return

        # Context Menu

        def hook__append_context_menu(
            webview: AnkiWebView, context_menu: QMenu
        ) -> None:
            """Appends quick-tags and other-tags sub-menu to the reviewer context-
            menu."""

            if aqt.mw.state != Key.REVIEW:  # type: ignore
                return

            note = get_reviewing_note()

            if note is None:
                return

            self._config.reload()

            context_menu.addSeparator()

            for tag in self._config.quick_tags:

                action = QAction(tag.name, context_menu)
                action.setCheckable(True)
                action.setChecked(note.has_tag(tag.name))
                action.toggled.connect(
                    functools.partial(
                        context_action__toggle_tag,
                        tag_name=tag.name,
                        note=note,
                    )
                )

                context_menu.addAction(action)

            if self._config.other_tags_are_visible:

                sub_menu = QMenu("Other tags...", context_menu)

                for tag in self._config.other_tags:

                    action = QAction(tag.name, sub_menu)
                    action.setCheckable(True)
                    action.setChecked(note.has_tag(tag.name))
                    action.toggled.connect(
                        functools.partial(
                            context_action__toggle_tag,
                            tag_name=tag.name,
                            note=note,
                        )
                    )

                    sub_menu.addAction(action)

                context_menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(hook__append_context_menu)

        # Shortcuts

        def hook__bind_shortcuts(
            state: str, shortcuts: list[tuple[str, Callable]]
        ) -> None:
            """Binds quick-tag shortcuts while reviewing cards."""

            if state != Key.REVIEW:
                return

            self._config.reload()

            for tag in self._config.quick_tags:

                shortcuts.append(
                    (
                        tag.shortcut,
                        functools.partial(
                            context_action__toggle_tag,
                            tag_name=tag.name,
                        ),
                    )
                )

        aqt.gui_hooks.state_shortcuts_will_change.append(hook__bind_shortcuts)

        def context_action__toggle_tag(tag_name: str, note: Note | None = None) -> None:
            """Toggles a tag within a Note."""

            # It's not always possible to access the current note when binding this
            # context action. For example, when binding the shortcuts, we cannot access
            # the note as the hook is triggered before a note is selected for review.
            # This provides a way to lazily get the currentl note in those cases.
            note = note if note is not None else get_reviewing_note()

            # It's possible that `note` is an Option[Note] here.
            if note is None:
                return

            if note.has_tag(tag_name):
                note.remove_tag(tag_name)
                aqt.utils.tooltip(f"Removed '{tag_name}'...")
            else:
                note.add_tag(tag_name)
                aqt.utils.tooltip(f"Added '{tag_name}'...")

            note.flush()

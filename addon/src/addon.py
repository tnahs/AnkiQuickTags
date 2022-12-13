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
            """Appends quick-tags and other-tags sub-menu to the reviewer context-menu.

            ┌─────────────────┐
            │ Copy            │
            │ Inspect         │
            ├─────────────────┤
            │ Tag-01          │
            │ Tag-02          │
            │ Tag-03          ├─────────────────┐
            │ Other tags... > │ Other-Tag-A     │
            └─────────────────┤ Other-Tag-B     │
                              │ Other-Tag-C     │
                              └─────────────────┘
            """

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
                        note=note,
                        tag_name=tag.name,
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
                            note=note,
                            tag_name=tag.name,
                        )
                    )

                    sub_menu.addAction(action)

                context_menu.addMenu(sub_menu)

        aqt.gui_hooks.webview_will_show_context_menu.append(hook__append_context_menu)

        # Shortcuts

        def hook__append_shortcuts(
            state: str, shortcuts: list[tuple[str, Callable]]
        ) -> None:
            """Appends quick-tag shortcuts while in the reviewing state."""

            if state != Key.REVIEW:
                return

            note = get_reviewing_note()

            if note is None:
                return

            self._config.reload()

            for tag in self._config.quick_tags:

                shortcuts.append(
                    (
                        tag.shortcut,
                        functools.partial(
                            context_action__toggle_tag,
                            note=note,
                            tag_name=tag.name,
                        ),
                    )
                )

        aqt.gui_hooks.state_shortcuts_will_change.append(hook__append_shortcuts)

        def context_action__toggle_tag(note: Note, tag_name: str) -> None:
            """Toggles a tag within a Note."""

            if note.has_tag(tag_name):
                note.remove_tag(tag_name)
                aqt.utils.tooltip(f"Removed '{tag_name}'...")
            else:
                note.add_tag(tag_name)
                aqt.utils.tooltip(f"Added '{tag_name}'...")

            note.flush()

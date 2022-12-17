from __future__ import annotations

import functools
from typing import Callable

import aqt
import aqt.gui_hooks
import aqt.utils
from anki.notes import Note
from aqt.editor import EditorWebView
from aqt.main import MainWebView
from aqt.qt.qt6 import QAction, QMenu

from .config import Config
from .helpers import Key, get_reviewing_note


class AnkiQuickTags:
    def __init__(self) -> None:
        self._config = Config()

    def setup(self) -> None:
        """Registers the add-on's hooks used to append context-menus and shortcuts."""

        if aqt.mw is None:
            return

        # The following functions are nested to prevent the need for declaring `self` as
        # the first argument in order to maintain the correct function signature while
        # still being able to access `self`.

        # Context Menus

        def hook__append_context_menu_reviewer(
            webview: MainWebView, context_menu: QMenu
        ) -> None:

            if aqt.mw.state != Key.REVIEW:  # type: ignore
                return

            note = get_reviewing_note()

            if note is None:
                return

            append_context_menu(
                webview=webview,
                context_menu=context_menu,
                note=note,
            )

        aqt.gui_hooks.webview_will_show_context_menu.append(
            hook__append_context_menu_reviewer
        )

        def hook__append_context_menu_editor(
            webview: EditorWebView, context_menu: QMenu
        ) -> None:

            if aqt.mw.state != Key.DECK_BROWSER:  # type: ignore
                return

            note = webview.editor.note

            if note is None:
                return

            append_context_menu(
                webview=webview,
                context_menu=context_menu,
                note=note,
            )

        aqt.gui_hooks.editor_will_show_context_menu.append(
            hook__append_context_menu_editor
        )

        def append_context_menu(
            webview: MainWebView | EditorWebView,
            context_menu: QMenu,
            note: Note,
        ) -> None:
            """Appends quick-tags and other-tags sub-menu to the context-menu."""

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
                        webview=webview,
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
                            webview=webview,
                        )
                    )

                    sub_menu.addAction(action)

                context_menu.addMenu(sub_menu)

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

        def context_action__toggle_tag(
            tag_name: str, webview: MainWebView | EditorWebView | None = None
        ) -> None:
            """Toggles a tag within a Note."""

            note: Note | None = None
            refresh: Callable | None = None

            # It's not always possible to access the current note when binding this
            # context action. For example, when binding shortcuts, we cannot access
            # the Note as the hook to bind them is triggered before Note is selected
            # for review.

            # User is reviewing cards.
            if isinstance(webview, MainWebView):
                note = get_reviewing_note()
                refresh = aqt.mw.reviewer._redraw_current_card  # type: ignore

            # User is editing cards.
            elif isinstance(webview, EditorWebView):
                note = webview.editor.note
                refresh = functools.partial(
                    webview.editor.set_note,
                    note=note,
                )

            # A shorcut is being bound.
            else:
                note = get_reviewing_note()

            # It's possible that `note` is still an Option[Note] here.
            if note is None:
                return

            if note.has_tag(tag_name):
                note.remove_tag(tag_name)
                aqt.utils.tooltip(f"Removed '{tag_name}'...")
            else:
                note.add_tag(tag_name)
                aqt.utils.tooltip(f"Added '{tag_name}'...")

            note.flush()

            if refresh is not None:
                refresh()

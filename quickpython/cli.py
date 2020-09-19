import asyncio
import os
import sys
from asyncio import Future, ensure_future
from pathlib import Path
from typing import Optional

import black
import isort
from prompt_toolkit import Application, widgets
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Float, FloatContainer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.search import start_search
from prompt_toolkit.shortcuts import clear, message_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.utils import Event
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
    toolbars,
)
from prompt_toolkit.widgets.base import Box, Button, Frame, Label

kb = KeyBindings()
eb = KeyBindings()
current_file: Optional[Path] = None

style = Style.from_dict(
    {
        "menu-bar": "bg:#aaaaaa black bold",
        "menu-bar.selected-item": "bg:black #aaaaaa bold",
        "menu": "bg:#aaaaaa black bold",
        "menu.border shadow": "black",
        "shadow": "bg:black",
        "dialog": "bg:#0000AA",
        "dialog frame.label": "fg:black bg:#AAAAAA",
        "dialog.body": "bg:#AAAAAA fg:#000000",
        "dialog shadow": "bg:#000000",
        "button": "bg:#AAAAAA fg:#000000",
    }
)


@kb.add("escape")
def _(event):
    """Focus the menu"""
    if event.app.layout.has_focus(root_container.window):
        event.app.layout.focus(code)
    else:
        event.app.layout.focus(root_container.window)


def format_code(contents: str) -> str:
    return black_format_code(isort_format_code(contents))


def isort_format_code(contents: str) -> str:
    return isort.code(contents, profile="black", float_to_top=True)


class TextInputDialog:
    def __init__(self, title="", label_text="", completer=None):
        self.future = Future()

        def accept_text(buf):
            app.layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept():
            self.future.set_result(self.text_area.text)

        def cancel():
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer, multiline=False, width=D(preferred=40), accept_handler=accept_text,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


async def show_dialog_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


@kb.add("c-o")
def open_file(event=None):
    async def coroutine():
        global current_file

        open_dialog = TextInputDialog(
            title="Open file", label_text="Enter the path of a file:", completer=PathCompleter(),
        )

        filename = await show_dialog_as_float(open_dialog)

        if filename is not None:
            current_file = Path(filename).resolve()
            try:
                with open(current_file, "r", encoding="utf8") as new_file_conent:
                    code.buffer.text = new_file_conent.read()
                    open_file_frame.title = str(current_file)
                feedback(f"Successfully opened {current_file}")
            except IOError as error:
                feedback(f"Error: {error}")

    ensure_future(coroutine())


def feedback(text):
    immediate.buffer.text = text


def black_format_code(contents: str) -> str:
    """Formats the given import section using black."""
    try:
        immediate.buffer.text = ""
        return black.format_file_contents(contents, fast=True, mode=black.FileMode(),)
    except black.NothingChanged:
        return contents
    except Exception as error:
        immediate.buffer.text = str(error)
        return contents


@kb.add("c-q")
def exit(event=None):
    """Triggers the request to close QPython cleanly."""
    app.exit()


@Condition
def is_code_focused() -> bool:
    return app.layout.has_focus(code)


@kb.add("tab")
def indent(event):
    event.app.current_buffer.insert_text("    ")


@kb.add("enter", filter=is_code_focused)
def enter(event):
    buffer = event.app.current_buffer
    buffer.insert_text("\n")

    old_cursor_position = buffer.cursor_position
    if old_cursor_position == 0:
        return

    end_position = buffer.text.rfind("\n", 0, old_cursor_position) + 1
    code, rest = buffer.text[:end_position], buffer.text[end_position:]
    if len(code) < 2 or (code[-1] == "\n" and code[-2] == "\n"):
        return

    formatted_code = format_code(code)
    difference = len(formatted_code) - len(code)
    buffer.text = formatted_code + rest
    buffer.cursor_position = old_cursor_position + difference


@kb.add("c-s")
def save_file(event=None):
    if not current_file:
        raise NotImplementedError("Put file save dialog here")
    buffer = event.app.current_buffer
    buffer.text = format_code(buffer.text)
    current_file.write_text(buffer.text, encoding="utf8")
    immediate.buffer.text = f"Successfully saved {current_file}"


async def _run_buffer():
    buffer_filename = f"{current_file or 'buffer'}.qpython"
    with open(buffer_filename, "w") as buffer_file:
        buffer_file.write(app.current_buffer.text)

    try:
        clear()
        await app.run_system_command(f'{sys.executable} "{buffer_filename}"')
    finally:
        os.remove(buffer_filename)


@kb.add("c-r")
@kb.add("f5")
def run_buffer(event):
    asyncio.ensure_future(_run_buffer())


def undo():
    code.buffer.undo()


def cut():
    data = code.buffer.cut_selection()
    app.clipboard.set_data(data)


def copy():
    data = code.buffer.copy_selection()
    app.clipboard.set_data(data)


def delete():
    code.buffer.cut_selection()


def paste():
    code.buffer.paste_clipboard_data(app.clipboard.get_data())


search_toolbar = SearchToolbar()
code = TextArea(
    scrollbar=True,
    wrap_lines=False,
    focus_on_click=True,
    line_numbers=True,
    search_field=search_toolbar,
)
open_file_frame = Frame(
    HSplit(
        [
            # One window that holds the BufferControl with the default buffer on
            # the left.
            code,
            # A vertical line in the middle. We explicitly specify the width, to
            # make sure that the layout engine will not try to divide the whole
            # width by three for all these windows. The window will simply fill its
            # content by repeating this character.
        ],
        style="bg:#0000AA fg:#AAAAAA bold",
    ),
    title="Untitled",
    style="bg:#0000AA fg:#AAAAAA bold",
)


def not_yet_implemented(event=None):
    raise NotImplementedError("Still need to implement handler for this event")


@kb.add("c-g")
def goto(event=None):
    async def coroutine():
        dialog = TextInputDialog(title="Go to line", label_text="Line number:")

        line_number = await show_dialog_as_float(dialog)

        try:
            line_number = int(line_number)
        except ValueError:
            feedback("Invalid line number")
        else:
            code.buffer.cursor_position = (
                code.buffer.document.translate_row_col_to_index(
                    line_number - 1, 0
                )
            )

    ensure_future(coroutine())


@kb.add("c-f")
def search(event=None):
    start_search(code.control)


def search_next():
    search_state = app.current_search_state

    cursor_position = code.buffer.get_search_position(search_state, include_current_position=False)
    code.buffer.cursor_position = cursor_position


immediate = TextArea()
root_container = MenuContainer(
    body=HSplit(
        [
            open_file_frame,
            search_toolbar,
            Frame(immediate, title="Immediate", height=5, style="bg:#0000AA fg:#AAAAAA bold",),
            VSplit(
                [Label(text=" F1 - Help"), Label(text="F5 or Ctrl+R - Run")],
                style="bg:#00AAAA fg:white bold",
                height=1,
            ),
        ]
    ),
    menu_items=[
        MenuItem(
            " File ",
            children=[
                MenuItem("New...", handler=not_yet_implemented),
                MenuItem("Open...", handler=open_file),
                MenuItem("Save", handler=save_file),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=exit),
            ],
        ),
        MenuItem(
            " Edit ",
            children=[
                MenuItem("Undo", handler=undo),
                MenuItem("Cut", handler=cut),
                MenuItem("Copy", handler=copy),
                MenuItem("Paste", handler=paste),
                MenuItem("Delete", handler=delete),
                MenuItem("-", disabled=True),
                MenuItem("Find", handler=search),
                MenuItem("Find next", handler=search_next),
                MenuItem("Replace"),
                MenuItem("Go To", handler=goto),
                MenuItem("Select All", handler=not_yet_implemented),
                MenuItem("Time/Date", handler=not_yet_implemented),
            ],
        ),
        MenuItem(" View ", children=[MenuItem("Status Bar", handler=not_yet_implemented)],),
        MenuItem(" Info ", children=[MenuItem("About", handler=not_yet_implemented)],),
    ],
    floats=[
        Float(xcursor=True, ycursor=True, content=CompletionsMenu(max_height=16, scroll_offset=1),),
    ],
    key_bindings=kb,
)


layout = Layout(root_container)

app: Application = Application(
    layout=layout,
    full_screen=True,
    mouse_support=True,
    style=style,
    enable_page_navigation_bindings=True,
)


def start(argv=None):
    global current_file

    argv = sys.argv if argv is None else argv
    if len(sys.argv) > 2:
        sys.exit("Usage: qpython [filename]")
    elif len(sys.argv) == 2:
        current_file = Path(sys.argv[1]).resolve()
        with current_file.open(encoding="utf8") as open_file:
            code.buffer.text = open_file.read()
            open_file_frame.title = str(current_file)
    else:
        message_dialog(
            title="Welcome to",
            text="""QuickPython version 0.0.2

Copyright (c) 2020 Timothy Crosley. Few rights reserved. MIT Licensed.
Simultanously distributed to the US and Canada. And you know, the rest of the world.

A productive parody.
""",
            style=style,
        ).run()

    app.layout.focus(code.buffer)
    app.run()


if __name__ == "__main__":
    start()

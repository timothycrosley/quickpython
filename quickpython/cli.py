import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import black
import isort
from prompt_toolkit import Application, widgets
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Float, FloatContainer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
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
current_file: Optional[Path] = None

style = Style.from_dict(
    {
        "menu-bar": "bg:#aaaaaa black bold",
        "menu-bar.selected-item": "bg:black #aaaaaa bold",
        "menu": "bg:#aaaaaa black bold",
        "menu.border shadow": "black",
        "shadow": "bg:black",
    }
)


@kb.add("escape")
@kb.add("c-m")
def _(event):
    """Focus the menu"""
    if event.app.layout.has_focus(root_container.window):
        event.app.layout.focus(code)
    else:
        event.app.layout.focus(root_container.window)


def format_code(contents: str) -> str:
    return black_format_code(isort_format_code(contents))


def isort_format_code(contents: str) -> str:
    return isort.code(contents, profile="black")


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


@kb.add("tab")
def indent(event):
    event.app.current_buffer.insert_text("    ")


@kb.add("enter")
def enter(event):
    buffer = event.app.current_buffer
    buffer.insert_text("\n")

    old_cursor_position = buffer.cursor_position
    if old_cursor_position == 0:
        return

    end_position = buffer.text.rfind("\n", 0, old_cursor_position) + 1
    code, rest = buffer.text[:end_position], buffer.text[end_position:]
    if code[-1] == "\n" and code[-2] == "\n":
        return

    formatted_code = format_code(code)
    difference = len(formatted_code) - len(code)
    buffer.text = formatted_code + rest
    buffer.cursor_position = old_cursor_position + difference


@kb.add("c-s")
def safe_file(event):
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


def search_text():
    pass


@kb.add("c-f")
def search(event):
    dialog = Dialog(
        modal=True,
        title="Find text",
        body=Label(text="YOUR_TEXT", dont_extend_height=True),
        buttons=[Button(text="BUTTON_TEXT", handler=search_text)],
    )

    root_container.floats.append(Float(content=dialog))


class MainEditor(TextArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer.on_text_changed = Event(self.buffer, self.format_code)

    def format_code(self, code):
        end_position = self.buffer.text.rfind("\n", 0, self.buffer.cursor_position) + 1
        code, rest = self.buffer.text[:end_position], self.buffer.text[end_position:]
        formatted_code = isort.code(code)
        difference = len(formatted_code) - len(code)
        self.buffer.cursor_position += difference
        self.buffer.text = formatted_code + rest


code = TextArea(scrollbar=True, wrap_lines=False, focus_on_click=True)
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


immediate = TextArea()
root_container = MenuContainer(
    body=HSplit(
        [
            open_file_frame,
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
                MenuItem("Open...", handler=not_yet_implemented),
                MenuItem("Save"),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=exit),
            ],
        ),
        MenuItem(
            " Edit ",
            children=[
                MenuItem("Undo", handler=not_yet_implemented),
                MenuItem("Cut", handler=not_yet_implemented),
                MenuItem("Copy", handler=not_yet_implemented),
                MenuItem("Paste", handler=not_yet_implemented),
                MenuItem("Delete", handler=not_yet_implemented),
                MenuItem("-", disabled=True),
                MenuItem("Find", handler=not_yet_implemented),
                MenuItem("Find next", handler=not_yet_implemented),
                MenuItem("Replace"),
                MenuItem("Go To", handler=not_yet_implemented),
                MenuItem("Select All", handler=not_yet_implemented),
                MenuItem("Time/Date", handler=not_yet_implemented),
            ],
        ),
        MenuItem(" View ", children=[MenuItem("Status Bar", handler=not_yet_implemented)],),
        MenuItem(" Info ", children=[MenuItem("About", handler=not_yet_implemented)],),
    ],
    floats=[],
)


layout = Layout(root_container)

app: Application = Application(
    layout=layout, full_screen=True, key_bindings=kb, mouse_support=True, style=style
)


dialog_style = Style.from_dict(
    {
        "dialog": "bg:#0000AA",
        "dialog frame.label": "fg:black bg:#AAAAAA",
        "dialog.body": "bg:#AAAAAA fg:#000000",
        "dialog shadow": "bg:#000000",
        "button": "bg:#AAAAAA fg:#000000",
    }
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
            style=dialog_style,
        ).run()

    app.layout.focus(code.buffer)
    app.run()


if __name__ == "__main__":
    start()

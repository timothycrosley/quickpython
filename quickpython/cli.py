import sys
from pathlib import Path
from typing import Optional

import black
import isort
from prompt_toolkit import Application, widgets
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.utils import Event
from prompt_toolkit.widgets import TextArea, toolbars
from prompt_toolkit.widgets.base import Box, Button, Frame, Label

kb = KeyBindings()
current_file: Optional[Path] = None


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
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()


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


immediate = TextArea()
root_container = HSplit(
    [
        VSplit(
            [Button(text="File"), Button(text="Edit")],
            height=1,
            style="bg:#AAAAAA fg:black bold",
        ),
        open_file_frame,
        Frame(
            immediate, title="Immediate", height=5, style="bg:#0000AA fg:#AAAAAA bold",
        ),
        VSplit([Label(text=" F1 - Help")], style="bg:#00AAAA fg:white bold", height=1),
    ]
)

layout = Layout(root_container)

app: Application = Application(
    layout=layout, full_screen=True, key_bindings=kb, mouse_support=True
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

    app.run()

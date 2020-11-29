import asyncio
import builtins
import os
import pydoc
import sys
import types
from asyncio import Future, ensure_future
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Optional

import black
import isort
from prompt_toolkit import Application
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import AnyFormattedText, Template
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import (
    AnyContainer,
    ConditionalContainer,
    Container,
    DynamicContainer,
    Float,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.dimension import AnyDimension, Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.search import start_search
from prompt_toolkit.shortcuts import clear, message_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Dialog, MenuContainer, MenuItem, SearchToolbar, TextArea
from prompt_toolkit.widgets.base import Border, Button, Label

from quickpython import __version__, extensions  # noqa

ABOUT_MESSAGE = f"""QuickPython version {__version__}

Copyright (c) 2020 Timothy Crosley. Few rights reserved. MIT Licensed.
Simultanously distributed to the US and Canada.
And you know, the rest of the world.

A productive parody.
Made in Seattle.
"""

kb = KeyBindings()
eb = KeyBindings()
current_file: Optional[Path] = None

default_isort_config = isort.Config(settings_path=os.getcwd())
if default_isort_config == isort.settings.DEFAULT_CONFIG:
    default_isort_config = isort.Config(profile="black", float_to_top=True)

default_black_config_file = black.find_pyproject_toml((os.getcwd(),))
if default_black_config_file:
    default_black_config = black.parse_pyproject_toml(default_black_config_file)
else:
    default_black_config = {}

isort_config: isort.Config = default_isort_config
black_config: dict = default_black_config

code_frame_style = Style.from_dict({"frame.label": "bg:#AAAAAA fg:#0000aa"})
style = Style.from_dict(
    {
        "menu-bar": "bg:#aaaaaa black bold",
        "menu-bar.selected-item": "bg:black #aaaaaa bold",
        "menu": "bg:#aaaaaa black bold",
        "menu.border shadow": "black",
        "shadow": "bg:black",
        "dialog": "bg:#0000AA",
        "frame.label": "fg:#AAAAAA bold",
        "dialog frame.label": "fg:black bold bg:#AAAAAA",
        "code-frame frame.label": "bg:#AAAAAA fg:#0000aa",
        "dialog.body": "bg:#AAAAAA fg:#000000",
        "dialog shadow": "bg:#000000",
        "scrollbar.background": "bg:#AAAAAA",
        "scrollbar.button": "bg:black fg:black",
        "scrollbar.arrow": "bg:#AAAAAA fg:black bold",
        "": "bg:#0000AA fg:#AAAAAA bold",
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
    return isort.code(contents, config=isort_config)


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
            completer=completer,
            multiline=False,
            width=Dimension(preferred=40),
            accept_handler=accept_text,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=Dimension(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog:
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=Dimension(preferred=80),
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
        global isort_config
        global black_config

        open_dialog = TextInputDialog(
            title="Open file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        filename = await show_dialog_as_float(open_dialog)

        if filename is not None:
            current_file = Path(filename).resolve()
            isort_config = isort.Config(settings_path=current_file.parent)
            black_config_file = black.find_pyproject_toml((str(current_file),))
            if black_config_file:
                black_config = black.parse_pyproject_toml(black_config_file)
            else:
                black_config = {}

            try:
                with open(current_file, "r", encoding="utf8") as new_file_conent:
                    code.buffer.text = new_file_conent.read()
                    open_file_frame.title = current_file.name
                feedback(f"Successfully opened {current_file}")
            except IOError as error:
                feedback(f"Error: {error}")

    ensure_future(coroutine())


def save_as_file():
    async def coroutine():
        global current_file
        global isort_config
        global black_config

        save_dialog = TextInputDialog(
            title="Save file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        filename = await show_dialog_as_float(save_dialog)

        if filename is not None:
            current_file = Path(filename).resolve()
            isort_config = isort.Config(settings_path=current_file.parent)
            black_config_file = black.find_pyproject_toml((str(current_file),))
            if black_config_file:
                black_config = black.parse_pyproject_toml(black_config_file)
            else:
                black_config = {}
            if not current_file.suffixes and not current_file.exists():
                current_file = current_file.with_suffix(".py")
            open_file_frame.title = current_file.name
            save_file()

    ensure_future(coroutine())


def feedback(text):
    immediate.buffer.text = text


def black_format_code(contents: str) -> str:
    """Formats the given import section using black."""
    try:
        immediate.buffer.text = ""
        return black.format_file_contents(contents, fast=True, mode=black.FileMode(**black_config))
    except black.NothingChanged:
        return contents
    except Exception as error:
        immediate.buffer.text = str(error)
        return contents


def new(content=""):
    """Creates a new file buffer."""
    global current_file
    global isort_config
    global black_config

    current_file = None
    isort_config = default_isort_config
    black_config = default_black_config
    code.buffer.text = content
    open_file_frame.title = "Untitled"
    feedback("")


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
    if current_file and ".py" not in current_file.suffixes and ".pyi" not in current_file.suffixes:
        return

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
        save_as_file()
        return

    buffer = app.current_buffer
    buffer.text = format_code(buffer.text)
    current_file.write_text(buffer.text, encoding="utf8")
    immediate.buffer.text = f"Successfully saved {current_file}"


async def _run_buffer(debug: bool = False):
    buffer_filename = f"{current_file or 'buffer'}.qpython"
    with open(buffer_filename, "w") as buffer_file:
        user_code = app.current_buffer.text
        if not user_code.endswith("\n"):
            user_code += "\n"
        with_qpython_injected = isort.code(user_code, add_imports=["import quickpython.extensions"])
        buffer_file.write(isort_format_code(with_qpython_injected))
        if debug:
            buffer_file.write("breakpoint()")

    try:
        clear()
        os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
        await app.run_system_command(f'{sys.executable} "{buffer_filename}"')
    finally:
        os.remove(buffer_filename)


async def _view_buffer():
    clear()
    await app.run_system_command("echo ''")


@kb.add("c-r")
@kb.add("f5")
def run_buffer(event=None):
    asyncio.ensure_future(_run_buffer())


def debug():
    asyncio.ensure_future(_run_buffer(debug=True))


def view_buffer(event=None):
    asyncio.ensure_future(_view_buffer())


@kb.add("c-z")
def undo(event=None):
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


@kb.add("c-a")
def select_all(event=None):
    code.buffer.cursor_position = 0
    code.buffer.start_selection()
    code.buffer.cursor_position = len(code.buffer.text)


def insert_time_and_date():
    code.buffer.insert_text(datetime.now().isoformat())


search_toolbar = SearchToolbar()
code = TextArea(
    scrollbar=True,
    wrap_lines=False,
    focus_on_click=True,
    line_numbers=True,
    search_field=search_toolbar,
)
code.window.right_margins[0].up_arrow_symbol = "↑"  # type: ignore
code.window.right_margins[0].down_arrow_symbol = "↓"  # type: ignore


class CodeFrame:
    """A custom frame for the quick python code container to match desired styling"""

    def __init__(
        self,
        body: AnyContainer,
        title: AnyFormattedText = "",
        style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        key_bindings: Optional[KeyBindings] = None,
        modal: bool = False,
    ) -> None:

        self.title = title
        self.body = body

        fill = partial(Window, style="class:frame.border")
        style = "class:frame " + style

        top_row_with_title = VSplit(
            [
                fill(width=1, height=1, char=Border.TOP_LEFT),
                fill(char=Border.HORIZONTAL),
                Label(
                    lambda: Template(" {} ").format(self.title),
                    style="class:frame.label",
                    dont_extend_width=True,
                ),
                fill(char=Border.HORIZONTAL),
                fill(width=1, height=1, char=Border.TOP_RIGHT),
            ],
            height=1,
        )

        top_row_without_title = VSplit(
            [
                fill(width=1, height=1, char=Border.TOP_LEFT),
                fill(char=Border.HORIZONTAL),
                fill(width=1, height=1, char=Border.TOP_RIGHT),
            ],
            height=1,
        )

        @Condition
        def has_title() -> bool:
            return bool(self.title)

        self.container = HSplit(
            [
                ConditionalContainer(content=top_row_with_title, filter=has_title),
                ConditionalContainer(content=top_row_without_title, filter=~has_title),
                VSplit(
                    [
                        fill(width=1, char=Border.VERTICAL),
                        DynamicContainer(lambda: self.body),
                        fill(width=1, char=Border.VERTICAL),
                        # Padding is required to make sure that if the content is
                        # too small, the right frame border is still aligned.
                    ],
                    padding=0,
                ),
            ],
            width=width,
            height=height,
            style=style,
            key_bindings=key_bindings,
            modal=modal,
        )

    def __pt_container__(self) -> Container:
        return self.container


class ImmediateFrame:
    """
    Draw a border around any container, optionally with a title text.
    Changing the title and body of the frame is possible at runtime by
    assigning to the `body` and `title` attributes of this class.
    :param body: Another container object.
    :param title: Text to be displayed in the top of the frame (can be formatted text).
    :param style: Style string to be applied to this widget.
    """

    def __init__(
        self,
        body: AnyContainer,
        title: AnyFormattedText = "",
        style: str = "",
        width: AnyDimension = None,
        height: AnyDimension = None,
        key_bindings: Optional[KeyBindings] = None,
        modal: bool = False,
    ) -> None:

        self.title = title
        self.body = body

        fill = partial(Window, style="class:frame.border")
        style = "class:frame " + style

        top_row_with_title = VSplit(
            [
                fill(width=1, height=1, char="├"),
                fill(char=Border.HORIZONTAL),
                # Notice: we use `Template` here, because `self.title` can be an
                # `HTML` object for instance.
                Label(
                    lambda: Template(" {} ").format(self.title),
                    style="class:frame.label",
                    dont_extend_width=True,
                ),
                fill(char=Border.HORIZONTAL),
                fill(width=1, height=1, char="┤"),
            ],
            height=1,
        )

        top_row_without_title = VSplit(
            [
                fill(width=1, height=1, char=Border.TOP_LEFT),
                fill(char=Border.HORIZONTAL),
                fill(width=1, height=1, char=Border.TOP_RIGHT),
            ],
            height=1,
        )

        @Condition
        def has_title() -> bool:
            return bool(self.title)

        self.container = HSplit(
            [
                ConditionalContainer(content=top_row_with_title, filter=has_title),
                ConditionalContainer(content=top_row_without_title, filter=~has_title),
                VSplit(
                    [
                        fill(width=1, char=Border.VERTICAL),
                        DynamicContainer(lambda: self.body),
                        fill(width=1, char=Border.VERTICAL),
                        # Padding is required to make sure that if the content is
                        # too small, the right frame border is still aligned.
                    ],
                    padding=0,
                ),
            ],
            width=width,
            height=height,
            style=style,
            key_bindings=key_bindings,
            modal=modal,
        )

    def __pt_container__(self) -> Container:
        return self.container


open_file_frame = CodeFrame(
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
    ),
    title="Untitled",
    style="class:code-frame",
)


@kb.add("c-g")
def goto(event=None):
    async def coroutine():
        dialog = TextInputDialog(title="Go to line", label_text="Line number:")

        line_number = await show_dialog_as_float(dialog)
        if line_number is None:
            return

        try:
            line_number = int(line_number)
        except ValueError:
            feedback("Invalid line number")
        else:
            code.buffer.cursor_position = code.buffer.document.translate_row_col_to_index(
                line_number - 1, 0
            )

    ensure_future(coroutine())


def replace_text():
    async def coroutine():
        to_replace_dialog = TextInputDialog(title="Text to Replace", label_text="original:")
        replacement_dialog = TextInputDialog(title="Replace With", label_text="replacement:")

        to_replace = await show_dialog_as_float(to_replace_dialog)
        if to_replace is None:
            return

        replacement = await show_dialog_as_float(replacement_dialog)
        if replacement is None:
            return

        code.buffer.text = format_code(code.buffer.text.replace(to_replace, replacement))

    ensure_future(coroutine())


def about():
    async def coroutine():
        await show_dialog_as_float(MessageDialog("About QuickPython", ABOUT_MESSAGE))

    ensure_future(coroutine())


def add_function():
    async def coroutine():
        dialog = TextInputDialog(title="Add Function", label_text="Function name:")

        function_name = await show_dialog_as_float(dialog)
        if not function_name:
            return

        code.buffer.insert_text(
            f"""
def {function_name}():
    pass
"""
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


def add_class():
    async def coroutine():
        dialog = TextInputDialog(title="Add Class", label_text="Class name:")

        class_name = await show_dialog_as_float(dialog)
        if not class_name:
            return

        code.buffer.insert_text(
            f"""
class {class_name}:
    def __init__(self):
        pass
"""
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


def add_data_class():
    async def coroutine():
        dialog = TextInputDialog(title="Add Data Class", label_text="Class name:")

        class_name = await show_dialog_as_float(dialog)
        if not class_name:
            return

        code.buffer.insert_text(
            f'''
@dataclass
class {class_name}:
    """Comment"""
'''
        )
        code.buffer.text = isort.code(
            code.buffer.text,
            add_imports=["from dataclasses import dataclass"],
            float_to_top=True,
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


def add_method():
    async def coroutine():
        dialog = TextInputDialog(title="Add Method", label_text="Method name:")

        method_name = await show_dialog_as_float(dialog)
        if not method_name:
            return

        code.buffer.insert_text(
            f"""
    def {method_name}(self):
        pass
"""
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


def add_static_method():
    async def coroutine():
        dialog = TextInputDialog(title="Add Static Method", label_text="Method name:")

        method_name = await show_dialog_as_float(dialog)
        if not method_name:
            return

        code.buffer.insert_text(
            f"""
    @staticmethod
    def {method_name}():
        pass
"""
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


def add_class_method():
    async def coroutine():
        dialog = TextInputDialog(title="Add Class Method", label_text="Method name:")

        method_name = await show_dialog_as_float(dialog)
        if not method_name:
            return

        code.buffer.insert_text(
            f"""
    @classmethod
    def {method_name}(cls):
        pass
"""
        )
        code.buffer.text = format_code(code.buffer.text)

    ensure_future(coroutine())


@kb.add("c-f")
def search(event=None):
    start_search(code.control)


def search_next(event=None):
    search_state = app.current_search_state

    cursor_position = code.buffer.get_search_position(search_state, include_current_position=False)
    code.buffer.cursor_position = cursor_position


def example(game_name: str):
    import inspect

    from quickpython import examples

    def expand_example():
        new(inspect.getsource(getattr(examples, game_name)))

    return expand_example


def built_in_functions():
    docs = [
        pydoc.render_doc(builtin, renderer=pydoc.plaintext).split("\n", 1)[1]
        for builtin_name, builtin in vars(builtins).items()
        if type(builtin) in (types.FunctionType, types.BuiltinFunctionType)
        and not builtin_name.startswith("_")
    ]
    new("\n".join(docs))


QLabel = partial(Label, dont_extend_width=True)
SPACE = QLabel(" ")

immediate = TextArea()
root_container = MenuContainer(
    body=HSplit(
        [
            open_file_frame,
            search_toolbar,
            ImmediateFrame(
                immediate,
                title="Immediate",
                height=5,
                style="fg:#AAAAAA bold",
            ),
            VSplit(
                [
                    QLabel("<F1=Help>"),
                    SPACE,
                    QLabel("<F5=Run>"),
                    SPACE,
                    QLabel("<CTRL+R=Run>"),
                ],
                style="bg:#00AAAA fg:white bold",
                height=1,
            ),
        ]
    ),
    menu_items=[
        MenuItem(
            " File ",
            children=[
                MenuItem("New...", handler=new),
                MenuItem("Open...", handler=open_file),
                MenuItem("Save", handler=save_file),
                MenuItem("Save as...", handler=save_as_file),
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
                MenuItem("Go To", handler=goto),
                MenuItem("Select All", handler=select_all),
                MenuItem("Add Time/Date", handler=insert_time_and_date),
                MenuItem("-", disabled=True),
                MenuItem("New Function", handler=add_function),
                MenuItem("New Class", handler=add_class),
                MenuItem("New Data Class", handler=add_data_class),
                MenuItem("New Method", handler=add_method),
                MenuItem("New Static Method", handler=add_static_method),
                MenuItem("New Class Method", handler=add_class_method),
            ],
        ),
        MenuItem(
            " View ",
            children=[MenuItem("Output Screen", handler=view_buffer)],
        ),
        MenuItem(
            " Search ",
            children=[
                MenuItem("Find (CTRL+F)", handler=search),
                MenuItem("Repeat last find", handler=search_next),
                MenuItem("Change", handler=replace_text),
            ],
        ),
        MenuItem(
            " Run ",
            children=[
                MenuItem("Start (F5)", handler=run_buffer),
                MenuItem("Debug", handler=debug),
            ],
        ),
        MenuItem(
            " Examples ",
            children=[
                MenuItem("Connect", handler=example("connect")),
                MenuItem("Eight Puzzle", handler=example("eightpuzzle")),
                MenuItem("Hang Man", handler=example("hangman")),
                MenuItem("Memory", handler=example("memory")),
                MenuItem("Minesweeper", handler=example("minesweeper")),
                MenuItem("Simon", handler=example("simon")),
                MenuItem("Tic Tac Toe", handler=example("tictactoe")),
                MenuItem("Towers", handler=example("towers")),
                MenuItem("Zig Zag", handler=example("zigzag")),
                MenuItem("Uno", handler=example("uno")),
            ],
        ),
        MenuItem(
            " Help ",
            children=[
                MenuItem("About", handler=about),
                MenuItem("Built-in Functions", handler=built_in_functions),
            ],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
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
    color_depth=ColorDepth.DEPTH_8_BIT,
)


def start(argv=None):
    global current_file
    global isort_config
    global black_config

    argv = sys.argv if argv is None else argv
    if len(sys.argv) > 2:
        sys.exit("Usage: qpython [filename]")
    elif len(sys.argv) == 2:
        current_file = Path(sys.argv[1]).resolve()
        isort_config = isort.Config(settings_path=current_file.parent)
        black_config_file = black.find_pyproject_toml((str(current_file),))
        if black_config_file:
            black_config = black.parse_pyproject_toml(black_config_file)
        else:
            black_config = {}

        open_file_frame.title = current_file.name
        if current_file.exists():
            with current_file.open(encoding="utf8") as open_file:
                code.buffer.text = open_file.read()
    else:
        message_dialog(
            title="Welcome to",
            text=ABOUT_MESSAGE,
            style=style,
        ).run()

    app.layout.focus(code.buffer)
    app.run()


if __name__ == "__main__":
    start()

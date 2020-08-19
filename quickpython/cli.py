from prompt_toolkit import Application, widgets
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea, toolbars
from prompt_toolkit.widgets.base import Box, Frame, Button

kb = KeyBindings()


@kb.add("c-q")
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()


@kb.add('tab')
def indent(event):
    event.app.current_buffer.insert_text('    ')


class MainEditor(TextEditor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.buffer.on_text_changed
        
    def format_code(self):
        


buffer1 = Buffer()  # Editable buffer.

root_container = HSplit(
    [
        Box(VSplit([Button(text="File"), Button(text="Edit")]), height=1, style="bg:#AAAAAA fg:black bold"),
        Frame(
            HSplit(
                [
                    # One window that holds the BufferControl with the default buffer on
                    # the left.
                    TextArea(scrollbar=True, wrap_lines=False, focus_on_click=True),
                    # A vertical line in the middle. We explicitly specify the width, to
                    # make sure that the layout engine will not try to divide the whole
                    # width by three for all these windows. The window will simply fill its
                    # content by repeating this character.
                ],
                style="bg:#0000AA fg:#AAAAAA bold",
            ),
            title="Untitled",
            style="bg:#0000AA fg:#AAAAAA bold",
        ),
        Frame(
            TextArea(),
            title="Immediate",
            height=10,
            style="bg:#0000AA fg:#AAAAAA bold",
        )
    ]
)

layout = Layout(root_container)

app = Application(layout=layout, full_screen=True, key_bindings=kb, mouse_support=True)


def start():
    app.run()

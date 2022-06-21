# flake8: noqa
"""
:copyright: (c) 2022 Viraj Kanwade
:license: All rights reserved
"""

# from ._version import get_versions
# __version__ = get_versions()['version']
# del get_versions
__version__ = "0.0.1"

import shutil
from platform import python_version

import click
from prompt_toolkit.application import Application
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea

# from pygments.lexers import JsonLexer
from .command_processor import Command, CommandProcessor


# Utilities
# ---------
def init_text():
    """Returns the introductory text applied to output when the app is launched."""
    return (
        '[wsh "{}"] (Python "{}")\n'.format(__version__, python_version())
        + '\nType "help" for more info, or "exit" to quit.\n'
        + "-" * shutil.get_terminal_size()[0]
    )


# Command Processor
command_processor = CommandProcessor()

# Output Field
# ------------
# output_field = TextArea(text=init_text(),
#                         lexer=PygmentsLexer(JsonLexer))
output_field = TextArea(text=init_text())


# Input Field
# -----------
def accept_handler(buf):
    """Callback method invoked when <ENTER> is pressed."""
    command_processor.accept_handler(buf, input_field, output_field)


command_completer = WordCompleter(
    [command.value for command in Command], ignore_case=True
)

# input_field = TextArea(height=1,
#                       prompt=u'>>> ',
#                        lexer=PygmentsLexer(JsonLexer),
#                        completer=command_completer,
#                       style='class:input-field',
#                       multiline=False,
#                       wrap_lines=False,
#                       accept_handler=accept_handler)
input_field = TextArea(
    height=1,
    prompt=">>> ",
    completer=command_completer,
    style="class:input-field",
    multiline=False,
    wrap_lines=False,
    accept_handler=accept_handler,
)

# Container
# ---------
container = HSplit(
    [output_field, Window(height=1, char="-", style="class:line"), input_field]
)

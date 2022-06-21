"""
:copyright: (c) 2022 Viraj Kanwade
:license: All rights reserved
"""

from prompt_toolkit.key_binding import KeyBindings

key_bindings = KeyBindings()


@key_bindings.add("c-c")
@key_bindings.add("c-q")
def _(event):
    "Pressing Ctrl-Q or Ctrl-C will exit the user interface."
    event.app.exit()

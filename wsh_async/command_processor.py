"""
:copyright: (c) 2022 Viraj Kanwade
:license: All rights reserved
"""

from enum import Enum, unique

from blinker import signal
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document


@unique
class Command(Enum):
    EXIT = "exit"
    NONE = ""
    SEND = "send"
    CLOSE = "close"
    HELP = "help"


class CommandProcessor:
    def __init__(self):
        self.senders = dict()
        self.receivers = dict()

    def process_command(self, command, argument, input_field, output_field):
        if command == Command.NONE:
            input_field.text = ""
        elif command == Command.EXIT:
            get_app().exit()
        elif command == Command.SEND:
            wsh_send = signal("wsh-async-send")
            wsh_send.send(self, data=argument)
        elif command == Command.CLOSE:
            wsh_close = signal("wsh-async-close")
            wsh_close.send(self)
        elif command == Command.HELP:
            self.show_help(output_field)

    def accept_handler(self, buf, input_field, output_field):
        """Callback method invoked when <ENTER> is pressed."""
        try:
            tokens = input_field.text.split(" ")

            raw_command, sep, argument = input_field.text.partition(" ")
            if raw_command in self.senders:
                wsh_send = signal("wsh-async-send")
                wsh_send.send(self, data=self.senders[raw_command](argument))
                return

            command = Command(tokens[0])
            self.process_command(command, argument, input_field, output_field)
        except ValueError:
            output = 'Command not found, type "help" to see available commands.'
            output = output_field.text + "\n" + output
            output_field.buffer.document = Document(
                text=output, cursor_position=len(output)
            )
        finally:
            input_field.text = ""

    def register_sender(self, name, command):
        """Register a new command as a sending function in the shell."""
        self.senders[name] = command

    def register_receiver(self, name, callback):
        """Register a new command as a receiving callback in the shell."""
        self.receivers[name] = callback

    def show_help(self, output_field):
        """Shows a help message that lists available commands."""
        output = """
        `exit`           - Exit the shell.
        `send <data>`    - Sends the given data to the server.
        `close`          - Close the connection to the server but dont exit.
        `help`           - Shows this help message.
        """
        output = output_field.text + "\n" + output
        output_field.buffer.document = Document(
            text=output, cursor_position=len(output)
        )

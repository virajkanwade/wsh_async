"""
:copyright: (c) 2022 Viraj Kanwade
:license: All rights reserved
"""

import asyncio
import shutil
from typing import Any, Callable, Optional, TypeVar
from urllib.parse import urlparse, urlunparse

from blinker import signal
from prompt_toolkit.document import Document
from wsproto import ConnectionType, Event, WSConnection
from wsproto.connection import ConnectionState
from wsproto.events import (
    AcceptConnection,
    CloseConnection,
    Ping,
    RejectConnection,
    Request,
    TextMessage,
)
from wsproto.frame_protocol import CloseReason

_SelfConnection = TypeVar("_SelfConnection", bound="Connection")


class Connection:
    @classmethod
    async def create(
        self,
        url: str,
        app: Any,
        receiver: Optional[Callable[[str, _SelfConnection], Any]] = None,
    ) -> None:
        self = Connection()

        self.url: str = url

        parts = urlparse(self.url)

        self.is_ssl: bool = True if parts.scheme == "wss" else False
        if parts.hostname is None:
            raise Exception(f"Could not resolve hostname from url % {self.url}")
        self.host: str = parts.hostname
        self.port: int = parts.port or (443 if self.is_ssl else 80)
        self.target: str = urlunparse(
            ("", "", parts.path, parts.params, parts.query, parts.fragment)
        )
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.ws = WSConnection(connection_type=ConnectionType.CLIENT)

        self.app: Any = app
        self.output = app.layout.container.children[0].content.buffer
        self.receiver: Optional[Callable[[str, _SelfConnection], Any]] = receiver

        signal("wsh-async-send").connect(self.send, weak=False)
        signal("wsh-async-close").connect(self.close, weak=False)

        await self.__send(Request(host=self.host, target=self.target))
        asyncio.create_task(self.__receive())
        # await self.__receive()

        return self

    def display(self, data, direction=None) -> None:
        """Outputs the given string to the UI."""
        if direction is None:
            cursor = ""
        elif direction == "in":
            cursor = "<<< "
        elif direction == "out":
            cursor = ">>> "
        output = self.output.text + "\n" + cursor + data
        self.output.document = Document(text=output, cursor_position=len(output))

    def info(self, data):
        """Output given string as info, which is a right justified text element."""
        width = shutil.get_terminal_size()[0]
        output = data.rjust(width)
        output = self.output.text + "\n" + output
        self.output.document = Document(text=output, cursor_position=len(output))

    async def __send(self, event: Event) -> None:
        if isinstance(event, TextMessage):
            self.display(event.data, direction="out")
        if self.ws.state == ConnectionState.CLOSED:
            self.info("connection closed. cannot send message")
            return
        self.writer.write(self.ws.send(event))

    async def __receive(self) -> None:
        while True:
            data = await self.reader.read(4096)
            if self.ws.state == ConnectionState.CLOSED:
                break
            self.ws.receive_data(data)
            await self.__handle_events()

    async def __handle_events(self) -> None:
        text = ""
        for event in self.ws.events():
            if isinstance(event, AcceptConnection):
                self.info(f"Connection established: {self.url}")
            elif isinstance(event, RejectConnection):
                self.info("Connection rejected")
            elif isinstance(event, CloseConnection):
                self.info(f"Connection closed: code={event.code} reason={event.reason}")
                await self.__send(event.response())
            elif isinstance(event, Ping):
                await self.__send(event.response())
            elif isinstance(event, TextMessage):
                text += event.data
                if event.message_finished:
                    self.display(text, "in")
                    text = ""
            else:
                print(event)

    def send(self, sender, data):
        if data:
            asyncio.create_task(self.__send(TextMessage(data=data)))

    def close(self, sender):
        self.info("close")
        if self.ws.state == ConnectionState.OPEN:
            asyncio.create_task(self.__send(CloseConnection(CloseReason.GOING_AWAY)))
        # self.writer.close()

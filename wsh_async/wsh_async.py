"""
:copyright: (c) 2022 Viraj Kanwade
:license: All rights reserved
"""

import asyncio

import click

from .app import app
from .connection import Connection
from .interface import command_processor


async def wsh_async(url: str) -> None:
    await Connection.create(url, app, None)
    await app.run_async()


@click.command()
@click.argument("url")
def wsh_async_run(url: str) -> None:
    asyncio.run(wsh_async(url))

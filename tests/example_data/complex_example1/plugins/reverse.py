import asyncio

from .base import Plugin


class ReversePlugin(Plugin):
    name = "reverse"

    async def process(self, data: str) -> str:
        await asyncio.sleep(0.1)
        return data[::-1]

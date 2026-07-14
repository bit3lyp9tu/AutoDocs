import asyncio

from .base import Plugin


class UppercasePlugin(Plugin):
    name = "uppercase"

    async def process(self, data: str) -> str:
        await asyncio.sleep(0.1)
        return data.upper()

from abc import ABC, abstractmethod


class Plugin(ABC):
    name: str

    @abstractmethod
    async def process(self, data: str) -> str:
        ...

from fluentogram.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self) -> None:
        super().__init__()

    async def close(self) -> None:
        pass

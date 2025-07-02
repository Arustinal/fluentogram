from typing import Any


class NatsStorageMock:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("NatsStorage is not implemented")


class KvTranslatorHubMock:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("KvTranslatorHub is not implemented")

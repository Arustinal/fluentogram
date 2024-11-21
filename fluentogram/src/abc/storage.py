# coding=utf-8
"""
An abstract base for the Storage object
"""
from abc import ABC, abstractmethod
from typing import Any


class AbstractStorage(ABC):

    @abstractmethod
    def __init__(self, kv, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def put(self, locale: str, key: str, value: Any, mapping_values: dict[str, Any]):
        """Creates or replaces an existing key/value"""
        raise NotImplementedError

    @abstractmethod
    def create(self, locale: str, key: str, value: Any, mapping_values: dict[str, Any]):
        """Create will add the key/value pair iff it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, locale: str, *keys):
        """Deletes all transmitted keys"""
        raise NotImplementedError

    @abstractmethod
    def listen(self, messages: dict[str, dict]) -> None:
        """Listen for new keys/values and updates them in TranslatorHub"""
        raise NotImplementedError
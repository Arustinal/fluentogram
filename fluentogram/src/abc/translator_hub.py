# coding=utf-8
"""
An abstract base for the Translator Hub and Key/Value Translator Hub objects
"""
import sys
from abc import ABC, abstractmethod
if sys.version_info >= (3, 11):
    from typing import Self, Any
else:
    from typing import Any
    from typing_extensions import Self

from fluentogram.src.abc.runner import AbstractTranslatorRunner
from fluentogram.src.abc.storage import AbstractStorage


class AbstractTranslatorsHub(ABC):
    """This class should contain a couple of translator objects, usually one object per one locale."""

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def get_translator_by_locale(self, locale: str) -> AbstractTranslatorRunner:
        """
        Returns a Translator object by selected locale
        """
        raise NotImplementedError

class AbstractKvTranslatorHub(AbstractTranslatorsHub, ABC):
    @abstractmethod
    def from_storage(self, kv_storage: AbstractStorage) -> Self:
        """
        Initializes the Translator Hub with the provided storage
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, locale: str, key: str, value: Any, mapping_values: dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    def create(self, locale: str, key: str, value: Any, mapping_values: dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    def delete(self, locale: str, *keys):
        raise NotImplementedError


"""An abstract base for the Translator Hub and Key/Value Translator Hub objects"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from fluentogram.abc.runner import AbstractTranslatorRunner


class AbstractTranslatorsHub(ABC):
    """This class should contain a couple of translator objects, usually one object per one locale."""

    def normalize_locales_map(self, locales_map: dict[str, str | Iterable[str]]) -> dict[str, Iterable[str]]:
        return {key: (value,) if isinstance(value, str) else value for key, value in locales_map.items()}

    @abstractmethod
    def get_translator_by_locale(self, locale: str) -> AbstractTranslatorRunner:
        """Returns a Translator object by selected locale"""
        raise NotImplementedError

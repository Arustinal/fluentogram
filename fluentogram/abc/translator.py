from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractTranslator(ABC):
    """A translator class, implements key-value interface for your translator mechanism."""

    @abstractmethod
    def __init__(self, locale: str, translator: Any, separator: str = "-") -> None:
        self.locale = locale
        self.separator = separator
        self.translator = translator

    @abstractmethod
    def get(self, key: str, **kwargs: Any) -> str | None:
        """Convert a translation key to a translated text string.
        Use kwargs dict to pass external data to the translator.
        Expects to be fast and furious.
        """
        raise NotImplementedError

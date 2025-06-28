"""An abstract base for storage implementations"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fluentogram.translator import FluentTranslator


class AbstractStorage(ABC):
    """Abstract storage for translators by locale."""

    @abstractmethod
    def add_translator(self, translator: FluentTranslator) -> None:
        """Add a translator to storage."""
        raise NotImplementedError

    @abstractmethod
    def add_translators(self, translators: Iterable[FluentTranslator]) -> None:
        """Add multiple translators to storage."""
        raise NotImplementedError

    @abstractmethod
    def get_translator(self, locale: str) -> FluentTranslator | None:
        """Get translator by locale."""
        raise NotImplementedError

    @abstractmethod
    def has_translator(self, locale: str) -> bool:
        """Check if translator exists for given locale."""
        raise NotImplementedError

    @abstractmethod
    def get_all_translators(self) -> Iterable[FluentTranslator]:
        """Get all translators from storage."""
        raise NotImplementedError

    @abstractmethod
    def get_translators_by_locales(self, locales: Iterable[str]) -> Iterable[FluentTranslator]:
        """Get translators by list of locales."""
        raise NotImplementedError

    @abstractmethod
    def get_translators_list(self) -> list[FluentTranslator]:
        """Get all translators as a list."""
        raise NotImplementedError

    @abstractmethod
    def set_locales_map(self, locales_map: dict[str, str | Iterable[str]]) -> None:
        """Set the locales mapping configuration."""
        raise NotImplementedError

    @abstractmethod
    def get_translators_map(self) -> dict[str, Iterable[FluentTranslator]]:
        """Get the translators map based on locales configuration."""
        raise NotImplementedError

    @abstractmethod
    def get_translators_for_language(self, language: str) -> Iterable[FluentTranslator]:
        """Get translators for a specific language based on locales map."""
        raise NotImplementedError

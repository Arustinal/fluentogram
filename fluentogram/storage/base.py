"""An abstract base for storage implementations"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fluentogram.translator import FluentTranslator


class BaseStorage(ABC):
    """Abstract storage for translators by locale."""

    def __init__(self) -> None:
        """Initialize storage with empty containers."""
        self._storage: dict[str, FluentTranslator] = {}
        self._locales_map: dict[str, Iterable[str]] = {}
        self._translators_map: dict[str, Iterable[FluentTranslator]] = {}

    def get_locales_map(self) -> dict[str, Iterable[str]]:
        """Get the locales mapping configuration."""
        return self._locales_map

    def add_translator(self, translator: FluentTranslator) -> None:
        """Add a translator to storage."""
        self._storage[translator.locale] = translator

    def add_translators(self, translators: Iterable[FluentTranslator]) -> None:
        """Add multiple translators to storage."""
        for translator in translators:
            self.add_translator(translator)

    def get_translator(self, locale: str) -> FluentTranslator | None:
        """Get translator by locale."""
        return self._storage.get(locale)

    def has_translator(self, locale: str) -> bool:
        """Check if translator exists for given locale."""
        return locale in self._storage

    def get_all_translators(self) -> Iterable[FluentTranslator]:
        """Get all translators from storage."""
        return self._storage.values()

    def get_translators_by_locales(self, locales: Iterable[str]) -> Iterable[FluentTranslator]:
        """Get translators by list of locales."""
        return tuple(self._storage[locale] for locale in locales if locale in self._storage)

    def get_translators_list(self) -> list[FluentTranslator]:
        """Get all translators as a list."""
        return list(self._storage.values())

    def set_locales_map(self, locales_map: Mapping[str, str | Iterable[str]]) -> None:
        """Set the locales mapping configuration."""
        # Normalize locales map (convert single strings to tuples)
        self._locales_map = {key: (value,) if isinstance(value, str) else value for key, value in locales_map.items()}
        # Rebuild translators map
        self._build_translators_map()

    def get_translators_map(self) -> dict[str, Iterable[FluentTranslator]]:
        """Get the translators map based on locales configuration."""
        return self._translators_map

    def get_translators_for_language(self, language: str) -> Iterable[FluentTranslator]:
        """Get translators for a specific language based on locales map."""
        return self._translators_map.get(language, ())

    def _build_translators_map(self) -> None:
        """Build the translators map based on locales configuration."""
        self._translators_map = {
            lang: self.get_translators_by_locales(translator_locales)
            for lang, translator_locales in self._locales_map.items()
        }

    async def update_translation(self, locale: str, key: str, value: str) -> bool:
        """Update a translation key for a specific locale."""
        translator = self._storage.get(locale)
        if translator is None:
            return False

        translator.update_translation(key, value)
        return True

    @abstractmethod
    async def close(self) -> None:
        pass

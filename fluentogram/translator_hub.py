from __future__ import annotations

from collections.abc import Iterable, Mapping

from fluentogram.exceptions import RootTranslatorNotFoundError
from fluentogram.runner import TranslatorRunner
from fluentogram.storage import BaseStorage, MemoryStorage
from fluentogram.translator import FluentTranslator


class TranslatorHub:
    """This class implements a storage for all single-locale translators."""

    def __init__(
        self,
        locales_map: Mapping[str, str | Iterable[str]],
        translators: list[FluentTranslator] | None = None,
        root_locale: str = "en",
        separator: str = "-",
        storage: BaseStorage | None = None,
    ) -> None:
        self.root_locale = root_locale
        self.separator = separator

        self.storage = storage or MemoryStorage()

        # Add translators to storage
        if translators is not None:
            self.storage.add_translators(translators)

        # Set locales map in storage
        self.storage.set_locales_map(locales_map)

        if not self.storage.has_translator(root_locale):
            raise RootTranslatorNotFoundError(self.root_locale)

    async def update_translation(self, locale: str, key: str, value: str) -> bool:
        """Update translation for a given locale and key."""
        return await self.storage.update_translation(locale, key, value)

    def get_translator_by_locale(self, locale: str) -> TranslatorRunner:
        """Here is a little tricky moment.
        There should be like a one-shot scheme.
        For proper isolation, function returns TranslatorRunner new instance every time, not the same translator.
        This trick makes "obj.attribute1.attribute2" access to be able.
        You are able to do what you want, refer to the abstract class.
        """
        translators = self.storage.get_translators_for_language(locale)
        if not translators:
            # Fallback to root locale
            translators = self.storage.get_translators_for_language(self.root_locale)

        return TranslatorRunner(
            translators=translators,
            separator=self.separator,
        )

    @property
    def translators(self) -> list[FluentTranslator]:
        """Get all translators from storage."""
        return self.storage.get_translators_list()

    @property
    def translators_map(self) -> dict[str, Iterable[FluentTranslator]]:
        """Get translators map from storage."""
        return self.storage.get_translators_map()

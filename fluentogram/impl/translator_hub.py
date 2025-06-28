"""A Translator Hub, using as factory for Translator objects"""

from __future__ import annotations

from collections.abc import Iterable

from fluentogram.abc import AbstractTranslator, AbstractTranslatorsHub
from fluentogram.exceptions import RootTranslatorNotFoundError
from fluentogram.impl import TranslatorRunner


class TranslatorHub(AbstractTranslatorsHub):
    """This class implements a storage for all single-locale translators."""

    def __init__(
        self,
        locales_map: dict[str, str | Iterable[str]],
        translators: list[AbstractTranslator],
        root_locale: str = "en",
        separator: str = "-",
    ) -> None:
        self.locales_map = self.normalize_locales_map(locales_map)
        self.translators = translators
        self.root_locale = root_locale
        self.separator = separator
        self.storage: dict[str, AbstractTranslator] = dict(
            zip([translator.locale for translator in translators], translators, strict=False),
        )
        if not self.storage.get(root_locale):
            raise RootTranslatorNotFoundError(self.root_locale)

        self.translators_map: dict[str, Iterable[AbstractTranslator]] = self._locales_map_parser(self.locales_map)

    def _locales_map_parser(
        self,
        locales_map: dict[str, str | Iterable[str]],
    ) -> dict[str, Iterable[AbstractTranslator]]:
        return {
            lang: tuple(self.storage[locale] for locale in translator_locales if locale in self.storage)
            for lang, translator_locales in locales_map.items()
        }

    def get_translator_by_locale(self, locale: str) -> TranslatorRunner:
        """Here is a little tricky moment.
        There should be like a one-shot scheme.
        For proper isolation, function returns TranslatorRunner new instance every time, not the same translator.
        This trick makes "obj.attribute1.attribute2" access to be able.
        You are able to do what you want, refer to the abstract class.
        """
        return TranslatorRunner(
            translators=self.translators_map.get(locale) or self.translators_map[self.root_locale],
            separator=self.separator,
        )

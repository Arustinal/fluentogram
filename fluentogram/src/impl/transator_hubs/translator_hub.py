# coding=utf-8
"""
A Translator Hub, using as factory for Translator objects
"""
from typing import Dict, Iterable, List, Union

from fluentogram.exceptions import NotImplementedRootLocaleTranslator
from fluentogram.src.abc import AbstractTranslator, AbstractTranslatorsHub
from fluentogram.src.impl import TranslatorRunner


class TranslatorHub(AbstractTranslatorsHub):
    """
    This class implements a storage for all single-locale translators.
    """

    def __init__(
            self,
            locales_map: Dict[str, Union[str, Iterable[str]]],
            translators: List[AbstractTranslator],
            root_locale: str = "en",
            separator: str = "-",
    ) -> None:
        self.locales_map = dict(
            zip(
                locales_map.keys(),
                map(
                    lambda lang: tuple([lang]) if isinstance(lang, str) else lang,
                    locales_map.values()
                )
            )
        )
        self.translators = translators
        self.root_locale = root_locale
        self.separator = separator
        self.storage: Dict[str, AbstractTranslator] = dict(
            zip([translator.locale for translator in translators], translators)
        )
        if not self.storage.get(root_locale):
            raise NotImplementedRootLocaleTranslator(self.root_locale)
        self.translators_map: Dict[str, Iterable[AbstractTranslator]] = self._locales_map_parser(self.locales_map)

    def _locales_map_parser(
            self,
            locales_map: Dict[str, Union[str, Iterable[str]]]
    ) -> Dict[str, Iterable[AbstractTranslator]]:
        return {
            lang: tuple(
                [self.storage.get(locale)
                 for locale in translator_locales if locale in self.storage.keys()]
            )
            for lang, translator_locales in
            locales_map.items()
        }

    def get_translator_by_locale(self, locale: str) -> TranslatorRunner:
        """
        Here is a little tricky moment.
        There should be like a one-shot scheme.
        For proper isolation, function returns TranslatorRunner new instance every time, not the same translator.
        This trick makes "obj.attribute1.attribute2" access to be able.
        You are able to do what you want, refer to the abstract class.
        """
        return TranslatorRunner(
            translators=self.translators_map.get(locale) or self.translators_map[self.root_locale],
            separator=self.separator
        )

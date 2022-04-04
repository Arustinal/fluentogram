# coding=utf-8
"""
A Translator Hub, using as factory for Translator objects
"""
from typing import Iterable, Dict, Union, List

from fluentogram.src.impl import TranslatorRunner
from fluentogram.exceptions import NotImplementedRootLocaleTranslator
from fluentogram.src.abc import AbstractTranslatorsHub
from fluentogram.src.abc.translator import TAbstractTranslator


class TranslatorHub(AbstractTranslatorsHub):
    """
    This class implements a storage for all single-locale translators.
    """

    def __init__(self,
                 locales_map: Dict[str, Union[str, Iterable[str]]],
                 translators: List[TAbstractTranslator],
                 root_locale: str = "en") -> None:
        self.locales_map = locales_map
        self.translators = translators
        self.root_locale = root_locale
        self.storage: Dict[str, TAbstractTranslator] = dict(
            zip([translator.locale for translator in translators], translators)
        )
        if not self.storage.get(root_locale):
            raise NotImplementedRootLocaleTranslator(self.root_locale)

    def get_translator_by_locale(self, locale: str) -> TranslatorRunner:
        """
        Here is a little tricky moment.
        There should be like a one-shot scheme.
        For proper isolation, function returns TranslatorRunner new instance every time, not the same translator.
        This trick makes "obj.attribute1.attribute2" access to be able.
        You are able to do what you want, refer to the abstract class.
        """
        translators = [self.storage.get(_locale) for _locale in self.locales_map.get(locale)]
        return TranslatorRunner(translators=translators)

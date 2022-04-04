# coding=utf-8
"""
A translator runner by itself
"""
from typing import TypeVar, List

from fluentogram.src.impl import AttribTracer, FluentTranslator

TTranslatorRunner = TypeVar("TTranslatorRunner", bound="TranslatorRunner")


class TranslatorRunner(AttribTracer):
    """This is one-shot per Telegram event translator with attrib tracer access way."""

    def __init__(self, translators: List[FluentTranslator]) -> None:
        super().__init__()
        self.translators = translators
        self.request_line = ""

    def get(self, key: str, **kwargs) -> str:
        """Faster, direct way to use translator, without sugar-like typing supported attribute access way"""
        return self._get_translation(key, **kwargs)

    def _get_translation(self, key, **kwargs):
        for translator in self.translators:
            try:
                return translator.get(key, **kwargs)
            except KeyError:
                continue

    def __call__(self, **kwargs) -> str:
        text = self._get_translation(self.request_line[:-1], **kwargs)
        self.request_line = ""
        return text

    def __getattr__(self, item: str) -> TTranslatorRunner:
        self.request_line += f"{item}{self.translators[0].separator}"
        return self

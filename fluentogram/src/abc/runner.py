# coding=utf-8
"""
An abstract translator runner
"""
from abc import ABC
from typing import Iterable

from fluentogram.src.abc import AbstractAttribTracer, AbstractTranslator


class AbstractTranslatorRunner(AbstractAttribTracer, ABC):
    """This is one-shot per Telegram event translator with attrib tracer access way."""

    def __init__(self, translators: Iterable[AbstractTranslator], separator: str = "-") -> None:
        super().__init__()
        self.translators = translators
        self.separator = separator
        self.request_line = ""

    def get(self, key: str, **kwargs) -> str:
        """Fastest, direct way to use translator, without sugar-like typing supported attribute access way"""

    def _get_translation(self, key, **kwargs) -> str:
        ...

    def __call__(self, **kwargs) -> str:
        ...

    def __getattr__(self, item: str) -> 'AbstractTranslatorRunner':
        ...

# coding=utf-8
"""
An abstract translator runner
"""
from abc import ABC, abstractmethod

from fluentogram.src.abc import AbstractAttribTracer


class AbstractTranslatorRunner(AbstractAttribTracer, ABC):
    """This is one-shot per Telegram event translator with attrib tracer access way."""

    @abstractmethod
    def get(self, key: str, **kwargs) -> str:
        """Fastest, direct way to use translator, without sugar-like typing supported attribute access way"""

    @abstractmethod
    def _get_translation(self, key, **kwargs) -> str:
        ...

    @abstractmethod
    def __call__(self, **kwargs) -> str:
        ...

    @abstractmethod
    def __getattr__(self, item: str) -> 'AbstractTranslatorRunner':
        ...

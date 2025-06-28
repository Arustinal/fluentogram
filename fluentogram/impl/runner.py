"""A translator runner by itself"""

from collections.abc import Iterable
from typing import Any

from fluentogram.abc import AbstractTranslator
from fluentogram.abc.runner import AbstractTranslatorRunner
from fluentogram.exceptions import KeyNotFoundError


class TranslatorRunner(AbstractTranslatorRunner):
    def __init__(self, translators: Iterable[AbstractTranslator], separator: str = "-") -> None:
        self.translators = translators
        self.separator = separator
        self.request_line = ""

    def get(self, key: str, **kwargs: Any) -> str:
        """Fastest, direct way to use translator, without sugar-like typing supported attribute access way"""
        return self._get_translation(key, **kwargs)

    def _get_translation(self, key: str, **kwargs: Any) -> str:
        for translator in self.translators:
            text = translator.get(key, **kwargs)
            if text is not None:
                return text

        raise KeyNotFoundError(key)

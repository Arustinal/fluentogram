"""A translator runner by itself"""

from collections.abc import Iterable
from typing import Any

from fluentogram.exceptions import KeyNotFoundError
from fluentogram.translator import FluentTranslator


class TranslatorRunner:
    def __init__(self, translators: Iterable[FluentTranslator], separator: str = "-") -> None:
        self.translators = translators
        self.separator = separator
        self._request_line = ""

    def get(self, key: str, **kwargs: Any) -> str:
        """Fastest, direct way to use translator, without sugar-like typing supported attribute access way"""
        return self._get_translation(key, **kwargs)

    def _get_translation(self, key: str, **kwargs: Any) -> str:
        for translator in self.translators:
            text = translator.get(key, **kwargs)
            if text is not None:
                return text

        raise KeyNotFoundError(key)

    def __getattr__(self, item: str) -> "TranslatorRunner":
        self._request_line += f"{item}{self.separator}"
        return self

    def __call__(self, **kwargs: Any) -> str:
        text = self._get_translation(self._request_line.rstrip(self.separator), **kwargs)
        self._request_line = ""
        return text

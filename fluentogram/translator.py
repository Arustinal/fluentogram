"""Fluent implementation of AbstractTranslator"""

from __future__ import annotations

from typing import Any

from fluent_compiler.bundle import FluentBundle
from fluent_compiler.compiler import compile_messages
from fluent_compiler.resource import FtlResource

from fluentogram.exceptions import FormatError


class FluentTranslator:
    """Single-locale Translator, implemented with fluent_compiler Bundles"""

    def __init__(self, locale: str, translator: FluentBundle, separator: str = "-") -> None:
        self.locale = locale
        self.translator = translator
        self.separator = separator

    def get(self, key: str, **kwargs: Any) -> str | None:
        """STR100: Calling format with insecure string.
        Route questions to --> https://github.com/django-ftl/fluent-compiler
        """
        try:
            text, errors = self.translator.format(key, kwargs)
            if errors:
                raise FormatError(errors.pop(), key)
        except KeyError:
            return None

        return text

    def update_translation(self, key: str, value: str) -> None:
        """Update a translation key for a specific locale."""
        self.translator._compiled_messages[key] = compile_messages(  # noqa: SLF001
            self.locale,
            [FtlResource.from_string(f"{key} = {value}")],
        ).message_functions[key]

    def __repr__(self) -> str:
        return f"<fluentogram.FluentTranslator instance, {self.locale!r}>"

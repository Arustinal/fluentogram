# coding=utf-8
"""
Fluent implementation of AbstractTranslator
"""

from fluent_compiler.bundle import FluentBundle

from fluentogram.src.abc import AbstractTranslator


class FluentTranslator(AbstractTranslator):
    """Single-locale Translator, implemented with fluent_compiler Bundles"""

    def __init__(self, locale: str, translator: FluentBundle, separator: str = "-"):
        self.locale = locale
        self.translator = translator
        self.separator = separator

    def get(self, key: str, **kwargs):
        """STR100: Calling format with insecure string.
        Route questions to --> https://github.com/django-ftl/fluent-compiler"""
        text, errors = self.translator.format(key, kwargs)
        if errors:
            raise errors.pop()
        return text

    def __repr__(self):
        return f"<fluentogram.FluentTranslator instance, \"{self.locale:}\">"

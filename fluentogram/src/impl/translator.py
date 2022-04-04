# coding=utf-8
"""
Fluent implementation of AbstractTranslator
"""

from fluent_compiler.bundle import FluentBundle

from fluentogram.structure.abstract.translator import AbstractTranslator


class FluentTranslator(AbstractTranslator):
    """Single-locale Translator, implemented with fluent_compiler Bundles"""
    def __init__(self, locale: str, translator: FluentBundle, separator: str = "-"):
        super().__init__(locale=locale, translator=translator, separator=separator)

    def get(self, key: str, **kwargs):
        """STR100: Calling format with insecure string.
        Route questions to --> https://github.com/django-ftl/fluent-compiler"""
        text, errors = self.translator.format(key, kwargs)
        if errors:
            raise errors.pop()
        return text

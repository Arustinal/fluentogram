# coding=utf-8
"""
An abstract base for the Translator Hub object
"""
from abc import ABC, abstractmethod

from fluentogram.src.abc.translator import TAbstractTranslator


class AbstractTranslatorsHub(ABC):
    """This class should contain a couple of translator objects, usually one object per one locale."""

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def get_translator_by_locale(self, locale: str) -> TAbstractTranslator:
        """
        Returns a Translator object by selected locale
        """
        raise NotImplementedError

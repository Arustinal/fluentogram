"""An abstract translator runner"""

from abc import ABC, abstractmethod
from typing import Any


class AbstractTranslatorRunner(ABC):
    """This is one-shot per Telegram event translator with attrib tracer access way."""

    @abstractmethod
    def get(self, key: str, **kwargs: Any) -> str:
        """Fastest, direct way to use translator, without sugar-like typing supported attribute access way"""

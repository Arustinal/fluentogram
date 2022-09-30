# coding=utf-8
"""
Some miscellaneous
"""

from abc import ABC, abstractmethod


class AbstractAttribTracer(ABC):
    """Implements a mechanism for tracing attributes access way.

    Like a pretty simple, external-typing supported version of the translator.get("some-key-for-translation")

    Equivalent to obj.some.key.for.translation(**some_kwargs)
    """

    @abstractmethod
    def __init__(self) -> None:
        self.request_line = ""

    @abstractmethod
    def _get_request_line(self) -> str:
        request_line = self.request_line
        self.request_line = ""
        return request_line

    @abstractmethod
    def __getattr__(self, item) -> 'AbstractAttribTracer':
        """
        This method exists to map the "obj.attrib1.attrib2" access to "attrib1-attrib2" key.
        """
        self.request_line += f"{item}{self.separator}"
        return self

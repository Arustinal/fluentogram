# coding=utf-8
"""
An AttribTracer implementation
"""

from fluentogram.src.abc import AbstractAttribTracer


class AttribTracer(AbstractAttribTracer):
    """Attribute tracer class for obj.attrib1.attrib2 access"""

    def __init__(self) -> None:
        self.request_line = ""

    def _get_request_line(self) -> str:
        request_line = self.request_line
        self.request_line = ""
        return request_line

    def __getattr__(self, item) -> 'AttribTracer':
        """
        This method exists to map the "obj.attrib1.attrib2" access to "attrib1-attrib2" key.
        """
        self.request_line += f"{item}{self.separator}"
        return self

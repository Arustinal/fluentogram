# coding=utf-8
"""
A DateTimeTransformer itself
"""
from datetime import datetime
from typing import Union

from fluent_compiler.types import fluent_date, FluentDateType, FluentNone

from fluentogram.src.abc import AbstractDataTransformer


class DateTimeTransformer(AbstractDataTransformer):
    """This transformer converts a default python datetime object to FluentDate
    Typings refer to https://github.com/tc39/ecma402
    """

    def __new__(
            cls,
            date: datetime,
            **kwargs
    ) -> Union[FluentDateType, FluentNone]:
        return fluent_date(
            date,
            **kwargs
        )

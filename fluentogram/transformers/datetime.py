"""A DateTimeTransformer itself"""

from __future__ import annotations

from datetime import datetime

from fluent_compiler.types import FluentDateType, FluentNone, fluent_date

from fluentogram.transformers.base import AbstractDataTransformer


class DateTimeTransformer(AbstractDataTransformer):
    """This transformer converts a default python datetime object to FluentDate
    Typings refer to https://github.com/tc39/ecma402
    """

    def __new__(
        cls,
        date: datetime,
        **kwargs,
    ) -> FluentDateType | FluentNone:
        return fluent_date(
            date,
            **kwargs,
        )

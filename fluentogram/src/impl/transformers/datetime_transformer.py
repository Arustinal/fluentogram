# coding=utf-8
"""
A DateTimeTransformer itself
"""
from datetime import datetime
from typing import Literal, Union

from fluent_compiler.types import fluent_date, FluentDateType, FluentNone

from fluentogram.misc import timezones
from fluentogram.src.abc import AbstractDataTransformer


class DateTimeTransformer(AbstractDataTransformer):
    """This transformer converts a default python datetime object to FluentDate
    Typings refer to https://github.com/tc39/ecma402
    """
    def __new__(cls,
                date: datetime,
                hour12: bool = False,
                weekday: Literal["narrow", "short", "long"] = "narrow",
                era: Literal["narrow", "short", "long"] = "narrow",
                year: Literal["2-digit", "numeric"] = "numeric",
                month: Literal["2-digit", "numeric", "narrow", "short", "long"] = "numeric",
                day: Literal["2-digit", "numeric"] = "numeric",
                hour: Literal["2-digit", "numeric"] = "numeric",
                minute: Literal["2-digit", "numeric"] = "numeric",
                second: Literal["2-digit", "numeric"] = "numeric",
                timezone: Literal[timezones] = "UTC",
                timezone_name: Literal["short", "long", "shortOffset",
                                       "longOffset", "shortGeneric", "longGeneric"] = "short",
                **kwargs) -> Union[FluentDateType, FluentNone]:
        return fluent_date(date, hour12=hour12, weekday=weekday, era=era, year=year, month=month, day=day, hour=hour,
                           minute=minute, second=second, timeZoneName=timezone_name, **kwargs)

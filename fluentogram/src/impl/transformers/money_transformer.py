# coding=utf-8
"""
A MoneyTransformer by itself
"""
from decimal import Decimal
from typing import Literal, Union

from fluent_compiler.types import fluent_number, FluentNumber, FluentNone

from fluentogram.src.abc import AbstractDataTransformer


class MoneyTransformer(AbstractDataTransformer):
    """This transformer converts a decimal object to FluentNumber with proper metadata.
    Typings refer to https://github.com/tc39/ecma402
    """

    def __new__(
        cls,
        amount: Decimal,
        currency: str,
        currency_display: Union[
            Literal["code"], Literal["symbol"], Literal["name"]
        ] = "code",
        use_grouping: bool = False,
        minimum_significant_digits: int = None,
        maximum_significant_digits: int = None,
        minimum_fraction_digits: int = None,
        maximum_fraction_digits: int = None,
        **kwargs
    ) -> Union[FluentNumber, FluentNone]:
        return fluent_number(
            amount,
            style="currency",
            currencyDisplay=currency_display,
            currency=currency,
            useGrouping=use_grouping,
            minimumSignificantDigits=minimum_significant_digits,
            maximumSignificantDigits=maximum_significant_digits,
            minimumFractionDigits=minimum_fraction_digits,
            maximumFractionDigits=maximum_fraction_digits,
            **kwargs
        )

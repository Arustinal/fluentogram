"""A MoneyTransformer by itself"""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from fluent_compiler.types import FluentNone, FluentNumber, fluent_number

from fluentogram.transformers.base import AbstractDataTransformer


class MoneyTransformer(AbstractDataTransformer):
    """This transformer converts a decimal object to FluentNumber with proper metadata.
    Typings refer to https://github.com/tc39/ecma402
    """

    def __new__(  # noqa: PLR0913
        cls,
        amount: Decimal,
        currency: str,
        currency_display: Literal["code", "symbol", "name"] = "code",
        use_grouping: bool = False,  # noqa: FBT002
        minimum_significant_digits: int | None = None,
        maximum_significant_digits: int | None = None,
        minimum_fraction_digits: int | None = None,
        maximum_fraction_digits: int | None = None,
        **kwargs,
    ) -> FluentNumber | FluentNone:
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
            **kwargs,
        )

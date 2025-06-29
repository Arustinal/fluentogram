from datetime import UTC, datetime
from decimal import Decimal

from fluent_compiler.bundle import FluentBundle

from fluentogram import DateTimeTransformer, FluentTranslator, MoneyTransformer, TranslatorHub


def test_date_transformer() -> None:
    translators = [
        FluentTranslator(
            "en",
            translator=FluentBundle.from_string(
                "en-US",
                "meeting-time = Meeting scheduled for { $date }",
                use_isolating=False,
            ),
        ),
    ]

    hub = TranslatorHub({"en": "en"}, translators)
    translator = hub.get_translator_by_locale("en")

    # Use DateTimeTransformer for proper date formatting
    meeting_date = datetime(2024, 1, 15, 14, 30, tzinfo=UTC)
    formatted_date = DateTimeTransformer(meeting_date, dateStyle="full", timeStyle="short")
    assert (
        translator.get(
            "meeting-time",
            date=formatted_date,
        )
        == "Meeting scheduled for Monday, January 15, 2024, 2:30 PM"
    )


def test_money_transformer() -> None:
    translators = [
        FluentTranslator(
            "en",
            translator=FluentBundle.from_string(
                "en-US",
                "amount-message = You have { $amount }",
                use_isolating=False,
            ),
        ),
    ]

    hub = TranslatorHub({"en": ("en")}, translators)
    translator = hub.get_translator_by_locale("en")

    amount = Decimal("123456.78")
    formatted_amount = MoneyTransformer(amount, currency="USD", currency_display="symbol")
    assert translator.get("amount-message", amount=formatted_amount) == "You have $123456.78"

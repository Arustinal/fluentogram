# coding=utf-8
import unittest
from datetime import datetime
from decimal import Decimal

from fluent_compiler.bundle import FluentBundle

from fluentogram import (
    FluentTranslator,
    TranslatorHub,
    TranslatorRunner,
    MoneyTransformer,
    DateTimeTransformer,
)


class BasicUsage(unittest.TestCase):
    def test_full_usage(self):
        example_ftl_file_content = """
welcome = Welcome to the fluent aiogram addon!
greet-by-name = Hello, { $user }!
shop-success-payment = Your money, { $amount }, has been sent successfully at { $dt }.
        """
        t_hub = TranslatorHub(
            {"ua": ("ua", "ru", "en"), "ru": ("ru", "en"), "en": ("en",)},
            translators=[
                FluentTranslator(
                    locale="en",
                    translator=FluentBundle.from_string(
                        "en-US", example_ftl_file_content, use_isolating=False
                    ),
                )
            ],
            root_locale="en",
        )
        translator_runner: TranslatorRunner = t_hub.get_translator_by_locale("en")
        print(
            translator_runner.welcome(),
            "\n",
            translator_runner.greet.by.name(user="Alex"),
            "\n",
            translator_runner.shop.success.payment(
                amount=MoneyTransformer(currency="$", amount=Decimal("500")),
                dt=DateTimeTransformer(datetime.now()),
            ),
        )

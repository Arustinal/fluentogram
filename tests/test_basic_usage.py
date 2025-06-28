import pytest
from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub
from fluentogram.exceptions import FormatError, KeyNotFoundError, RootTranslatorNotFoundError


def test_basic_usage() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello"),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    assert translator.get("start-hello") == "Hello"


def test_basic_usage_with_args() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello, { $username }", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    assert translator.get("start-hello", username="Alex") == "Hello, Alex"


def test_fallback_to_default_locale() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
            "ru": ("ru", "en"),
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello, { $username }", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("ru")
    assert translator.get("start-hello", username="Alex") == "Hello, Alex"


def test_with_full_locales() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
            "ru": ("ru", "en"),
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string(
                    "en-US",
                    "start-hello = Hello, { $username }",
                    use_isolating=False,
                ),
            ),
            FluentTranslator(
                "ru",
                translator=FluentBundle.from_string(
                    "ru-RU",
                    "start-hello = Привет, { $username }",
                    use_isolating=False,
                ),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("ru")
    assert translator.get("start-hello", username="Alex") == "Привет, Alex"


def test_when_translation_not_found() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    with pytest.raises(KeyNotFoundError):
        translator.get("start-hello1", username="Alex")


def test_when_root_translator_not_provided() -> None:
    with pytest.raises(RootTranslatorNotFoundError):
        TranslatorHub(
            {
                "en": "en",
            },
            [
                FluentTranslator(
                    "ru",
                    translator=FluentBundle.from_string("ru-RU", "start-hello = Привет", use_isolating=False),
                ),
            ],
        )


def test_formatting_error() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello, { $username }", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    with pytest.raises(FormatError):
        translator.get("start-hello", username1="Alex")

def test_get_text_by_attribute() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    assert translator.start.hello() == "Hello"

def test_get_text_by_attribute_not_found() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello = Hello", use_isolating=False),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("en")
    with pytest.raises(KeyNotFoundError):
        translator.start.hello1()

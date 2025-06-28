from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub


def test_update_translation() -> None:
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

    translator_hub.storage.update_translation("en", "start-hello1", "Hello123")
    assert translator.get("start-hello1") == "Hello123"


def test_update_translation_after_fallback() -> None:
    translator_hub = TranslatorHub(
        {
            "en": "en",
            "ru": ("ru", "en"),
        },
        [
            FluentTranslator(
                "en",
                translator=FluentBundle.from_string("en-US", "start-hello1 = Hello1"),
            ),
            FluentTranslator(
                "ru",
                translator=FluentBundle.from_string("ru-RU", "start-hello = Привет"),
            ),
        ],
    )
    translator = translator_hub.get_translator_by_locale("ru")
    assert translator.get("start-hello1") == "Hello1"

    translator_hub.storage.update_translation("ru", "start-hello1", "Привет1")
    assert translator.get("start-hello1") == "Привет1"

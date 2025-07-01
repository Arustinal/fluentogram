import pytest
from fluent_compiler.bundle import FluentBundle

from fluentogram.exceptions import LocalesNotFoundError
from fluentogram.storage import FileStorage
from fluentogram.translator import FluentTranslator
from fluentogram.translator_hub import TranslatorHub


def test_file_storage() -> None:
    storage = FileStorage("tests/assets/locales/{locale}/")
    hub = TranslatorHub(
        {
            "en": "en",
        },
        storage=storage,
    )
    translator = hub.get_translator_by_locale("en")
    assert translator.get("hello") == "Hello, world!"


def test_file_storage_if_translators_passed() -> None:
    storage = FileStorage("tests/assets/locales/{locale}/")
    hub = TranslatorHub(
        {
            "en": "en",
        },
        translators=[
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_string("en", "hello = Hello, world1!"),
            ),
        ],
        storage=storage,
    )
    translator = hub.get_translator_by_locale("en")
    assert translator.get("hello") == "Hello, world1!"


def test_file_storage_if_no_locales_found() -> None:
    with pytest.raises(LocalesNotFoundError):
        FileStorage("tests")

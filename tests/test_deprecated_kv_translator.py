import pytest
from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator
from fluentogram.src.impl.transator_hubs import KvTranslatorHub


def test_deprecated_msg_kv_translator() -> None:
    with pytest.warns(DeprecationWarning):
        KvTranslatorHub(
            {
                "ru": ("ru", "en"),
                "en": ("en",),
            },
            translators=[
                FluentTranslator(
                    locale="en",
                    translator=FluentBundle.from_string(locale="en-US", text="hello = Hello {$name}!"),
                ),
                FluentTranslator(
                    locale="ru",
                    translator=FluentBundle.from_string(locale="ru", text="hello = Привет {$name}!"),
                ),
            ],
        )

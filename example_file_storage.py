"""Example usage of FileStorage with fluentogram"""

import asyncio

from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub
from fluentogram.storage.file import FileStorage


async def main():
    # Create FileStorage with custom path
    storage = FileStorage("my_translations")

    # Create translators for different locales
    translators = [
        FluentTranslator(
            "en",
            translator=FluentBundle.from_string(
                "en-US",
                "welcome = Welcome, { $username }!\nitems-count = You have { $count } items\nhello = Hello!",
            ),
        ),
        FluentTranslator(
            "ru",
            translator=FluentBundle.from_string(
                "ru-RU",
                "welcome = Добро пожаловать, { $username }!\nitems-count = У вас { $count } элементов\nhello = Привет!",
            ),
        ),
    ]

    # Add translators to storage (this will save them to files)
    storage.add_translators(translators)

    # Configure locale mapping with fallbacks
    locales_map = {
        "en": "en",
        "ru": ("ru", "en"),
    }

    # Set locales map in storage
    storage.set_locales_map(locales_map)

    # Create the translator hub using storage
    hub = TranslatorHub(locales_map, storage.get_translators_list())

    # Get translators and use them
    en_translator = hub.get_translator_by_locale("en")
    ru_translator = hub.get_translator_by_locale("ru")

    print("English translations:")
    print(en_translator.get("welcome", username="Alice"))
    print(en_translator.get("items-count", count=5))
    print(en_translator.get("hello"))

    print("\nRussian translations:")
    print(ru_translator.get("welcome", username="Алиса"))
    print(ru_translator.get("items-count", count=5))
    print(ru_translator.get("hello"))

    # Update a translation
    print("\nUpdating translation...")
    success = await storage.update_translation("en", "hello", "Updated Hello!")
    if success:
        print("Translation updated successfully!")

        # Get updated translator
        updated_en_translator = hub.get_translator_by_locale("en")
        print(f"Updated: {updated_en_translator.get('hello')}")

    # Get storage information
    info = storage.get_storage_info()
    print(f"\nStorage info: {info}")

    # Close storage (saves any pending changes)
    await storage.close()

    print("\nTranslations saved to files in 'my_translations' directory!")


if __name__ == "__main__":
    asyncio.run(main())

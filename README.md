# fluentogram

fluentogram is easy way to use i18n (<a href='https://projectfluent.org/'>Fluent</a>) mechanism in any python app.

## Features

- Customizable storage: You can implement your own storage to save translates.
- Fallback support: Automatic fallback to root locale when translations are missing.
- Precompiled fluent messages using <a href='https://github.com/django-ftl/fluent-compiler'>fluent_compiler</a> makes formatting messages faster.
- Dot access to messages: `translator.hello(name='Alex')`
- Stub generator

## Installation

```bash
pip install fluentogram
```

## Quick Start

### Basic Usage

```python
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

# Create translators for different locales
translators = [
    FluentTranslator(
        "en",
        translator=FluentBundle.from_string(
            "en-US",
            "welcome = Welcome, { $username }!\n"
            "items-count = You have { $count } items",
        ),
    ),
]

# Configure locale mapping with fallbacks
locales_map = {
    "en": "en",
}

# Create the translator hub
hub = TranslatorHub(locales_map, translators)

# Get a translator for a specific locale
translator = hub.get_translator_by_locale("en")

# Use translations
print(translator.get("welcome", username="Alice"))  # "Welcome, Alice!"
```

### Attribute-based Access

Fluentogram supports a convenient attribute-based syntax for accessing translations:

```python
print(translator.welcome(username="Alice"))        # "Welcome, Alice!"
print(translator.items.count(count=5))            # "You have 5 items"
```

### Stub generator with CLI

#### Install with CLI dependencies

```sh
pip install fluentogram[cli]
```

#### Run generator

```sh
fluentogram -f tests/assets/test.ftl -o test.pyi
```

## Storages

### File storage

```python
from fluentogram import TranslatorHub
from fluentogram.storage.file import FileStorage

# Create FileStorage with custom path
storage = FileStorage("my_translations/{locale}/")

locales_map = {
    "en": "en",
}

hub = TranslatorHub(locales_map, storage=storage)

translator = hub.get_translator_by_locale("en")

print(translator.get("hello"))  # Hello, world!
```

## fluentogram supports real-time translation updates using NATS KV storage:

Install:

```sh
pip install fluentogram[nats]
```

```python
import asyncio

from fluent_compiler.bundle import FluentBundle
from nats.js.api import KeyValueConfig, StorageType

from fluentogram import FluentTranslator, TranslatorHub
from fluentogram.nats.storage import NatsKvStorage


async def main():
    # Configure NATS KV storage
    kv_config = KeyValueConfig(
        bucket="fluentogram",
        storage=StorageType.FILE,
    )

    # Create NATS storage
    storage = await NatsKvStorage.from_servers(
        servers=["nats://localhost:4222"],
        kv_config=kv_config,
    )

    # Create translators
    translators = [
        FluentTranslator(
            "en",
            translator=FluentBundle.from_string(
                "en-US",
                "greeting = Hello, { $name }!",
            ),
        ),
    ]

    # Create hub with NATS storage
    hub = TranslatorHub(
        {"en": "en"},
        translators,
        storage=storage,
    )

    translator = hub.get_translator_by_locale("en")
    print(translator.get("greeting", name="World"))  # "Hello, World!"

    # Update translation dynamically
    await storage.update_translation("en", "greeting", "Hi there, { $name }!")

    # Wait for the update to propagate
    await asyncio.sleep(1)

    # Get updated translation
    print(translator.get("greeting", name="World"))  # "Hi there, World!"

    await storage.close()


asyncio.run(main())
```

## Error Handling

Fluentogram provides comprehensive error handling:

```python
from fluentogram.exceptions import KeyNotFoundError, FormatError, RootTranslatorNotFoundError

try:
    translator = hub.get_translator_by_locale("fr")
    result = translator.get("nonexistent-key")
except KeyNotFoundError as e:
    print(f"Translation key not found: {e.key}")
except RootTranslatorNotFoundError as e:
    print(f"Root locale translator missing: {e.root_locale}")
except FormatError as e:
    print(f"Formatting error for key {e.key}: {e.original_error}")
```

# Inside of fluentogram

### TranslatorHub

`TranslatorHub` is unit of distribution TranslatorRunner's.

Init:

```python
def __init__(
    self,
    locales_map: dict[str, str | Iterable[str]],
    translators: list[FluentTranslator],
    root_locale: str = "en",
) -> None:
```

### Locales map 

That's like a configuration map for "Rollback" feature. If you haven't configured translation for current locale - first in collection, "Rollback" will look to others locales' data and try to find a translation

For example:

```python
locales_map = {
    "ua": ("ua", "de", "en"),
    "de": ("de", "en"),
    "en": ("en",)
}
```

Let's look at this example

If translator does not find a translation for `ua` locale in `ua` data, next stop is `de` data. If it's failed too - it will look to `en` translations.

### Translators

You have 3 variants to use translators:

- In memory

```python
translators = [
    FluentTranslator(
        "en",
        translator=FluentBundle.from_string(
            "en-US",
            "welcome = Welcome, { $username }!\n"
            "items-count = You have { $count } items",
        ),
    ),
]
hub = TranslatorHub(locales_map, translators)
```

- From files using file storage
- From NATS KV using storage

[↑ Back to Storages](#storages)

# TranslatorHub

TranslatorHub is unit of distribution TranslatorRunner's.

Init:

```python
def __init__(
        self,
        locales_map: Dict[str, Union[str, Iterable[str]]],
        translators: List[TAbstractTranslator],
        root_locale: str = "en",
) -> None:
```

*Locales map* - that's like a configuration map for "Rollback" feature. If you haven't configured translation for
current locale - first in collection,
"Rollback" will look to others locales' data and try to find a translation

For example:

```python
locales_map = {
    "ua": ("ua", "de", "en"),
    "de": ("de", "en"),
    "en": ("en",)
}
```

Let's look at this example

If translator does not find a translation for "ua" locale in "ua" data, next stop is "de" data. If it's failed too - it
will look to "en" translations.

*Translators* - List of translator instances. Every translator has only one locale. Refer to "Translator" doc page.
First parameter - telegram locale. Pay attention to format of them. Hub's
method `def get_translator_by_locale(self, locale: str)` will use this parameter as key to find translator.

Example:

```python
FluentTranslator("en", translator=FluentBundle.from_files("en-US", filenames=[".../main.ftl"])),
```

"Wait, what about no-files configuration?" may you ask. This is OK too, because you should just choose another option
from FluentBundle:

```python
FluentTranslator("de", translator=FluentBundle.from_string("your*ftl*content"))
```

Get your strings from anywhere - Databases, Files, no matter the source.

*Root locale* - if fluentogram will meet unknown locale - this locale will be used for getting translation.

Pretty simple
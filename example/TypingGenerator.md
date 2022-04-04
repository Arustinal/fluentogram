After installation, use:

`i18n -ftl example.ftl -stub stub.py`

By default, `stub.py` will contain `TranslatorRunner` class with type hints for translation keys.

Avoid FTL syntax like:

`some-key = Sample text` and
`some-key-name = Sample text, name!`

Translator by itself will be OK with that, but typing generator's parser will raise error, because some keys should be a common point, not a completed translation key by itself.
Replace example with:

`some-key-base = Sample text` 
`some-key-name = Sample text, name!`

Still, stub generator in an alpha version.
Check the result file, and for good, paste variables types, used in translations.

class FluentogramError(Exception):
    pass


class RootTranslatorNotFoundError(FluentogramError):
    def __init__(self, root_locale: str) -> None:
        self.root_locale = root_locale
        super().__init__(
            f"TranslatorHub does not have a root locale translator. "
            f"Root locale is {self.root_locale!r}, provide translator with this locale.",
        )


class KeyNotFoundError(FluentogramError):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"Key {self.key!r} not found in translators")


class FormatError(FluentogramError):
    def __init__(self, original_error: Exception, key: str) -> None:
        self.original_error = original_error
        self.key = key
        super().__init__(f"Error formatting key: {self.key!r}: {self.original_error!r}")


class LocalesNotFoundError(FluentogramError):
    def __init__(self, locales: list[str], path: str) -> None:
        self.locales = locales
        self.path = path
        super().__init__(f"No locales found in {self.path}")

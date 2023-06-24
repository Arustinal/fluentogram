from typing import Optional, cast, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message
from fluentogram import TranslatorRunner


DEFAULT_TRANSLATOR_KEY = "i18n"


class FText(BaseFilter):
    translator_key = DEFAULT_TRANSLATOR_KEY

    def __init__(
        self, *,
        equals: Optional[str] = None,
        contains: Optional[str] = None,
        startswith: Optional[str] = None,
        endswith: Optional[str] = None,
        ignore_case: bool = False,
        translator_key: Optional[str] = None
    ) -> None:
        """
        Fluentogram text filter in the spirit of the deprecated aiogram Text filter.

        Usage example:
            @router.message(FText(equals="command-help"))
            async def helpCommand(message: Message, i18n: TranslatorRunner) -> TelegramMethod[Any]:
                return message.answer(i18n.help())
        """
        self.equals = equals
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
        self.ignore_case = ignore_case

        if translator_key:
            self.translator_key = translator_key

    async def __call__(
        self, event: Message, **data: Any
    ) -> bool:
        text = event.text or event.caption
        if text is not None:
            i18n: Optional[TranslatorRunner] = data.get(self.translator_key)
            if i18n is None:
                raise RuntimeError(
                    f"TranslatorRunner not found for key '{self.translator_key}'."
                )
            if self.ignore_case:
                text = text.casefold()

            if self.equals:
                return cast(bool, text == i18n.get(self.equals))  # lmao idk what he wants but mypy can't see bool here
            if self.contains:
                return i18n.get(self.contains) in text
            if self.startswith:
                return text.startswith(i18n.get(self.startswith))
            if self.endswith:
                return text.endswith(i18n.get(self.endswith))

        return False

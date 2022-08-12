import asyncio
import os
from typing import TYPE_CHECKING, Callable, Dict, Any, Awaitable

from aiogram import Bot, Dispatcher, Router, BaseMiddleware
from aiogram.types import Message
from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub, TranslatorRunner

if TYPE_CHECKING:
    from stub import TranslatorRunner  # you haven't this file until you use TypingGenerator


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        hub: TranslatorHub = data.get('_translator_hub')
        # There you can ask your database for locale
        data['i18n'] = hub.get_translator_by_locale(event.from_user.language_code)
        return await handler(event, data)


main_router = Router()
main_router.message.middleware(TranslatorRunnerMiddleware())


@main_router.message()
async def handler(message: Message, i18n: TranslatorRunner):
    await message.answer(i18n.start.hello(username=message.from_user.username))


async def main():
    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en",)
        },
        [
            FluentTranslator("en", translator=FluentBundle.from_string("en-US", "start-hello = Hello, { $username }")),
            FluentTranslator("ru", translator=FluentBundle.from_string("ru", "start-hello = Привет, { $username }"))
        ],
    )
    bot = Bot(token=os.getenv("TOKEN"))
    dp = Dispatcher()
    dp.include_router(main_router)
    print("bot is ready")
    await dp.start_polling(bot, _translator_hub=translator_hub)


if __name__ == '__main__':
    asyncio.run(main())

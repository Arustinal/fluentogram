After installation, use:

`i18n -ftl example.ftl -stub stub.pyi`

By default, `stub.py` will contain `TranslatorRunner` class with type hints for translation keys.

Usage in files:

```py
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message
from fluentogram import TranslatorRunner

if TYPE_CHECKING:
    from stub import TranslatorRunner

router = Router()


@router.message()
async def handler(message: Message, i18n: TranslatorRunner):
    await message.answer(
        i18n.hello(username=message.from_user.username)
    )
```

stub.pyi - result file after stub generator
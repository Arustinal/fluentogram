# TranslatorRunner

TranslatorRunner is a key component of Fluentogram

This single-per-message unit executes translation request

Like that:

```python
@router.message()
async def handler(message: Message, i18n: TranslatorRunner):
    await message.answer(
        i18n.say.hello(username=message.from_user.username)
    )
```

FTL content:

```text
say-hello = "Hello { $username}!"
```

So, as can you see, i18n is instance of TranslatorRunner, created in middleware before the message handler.

Note: *Any variables for TranslatorRunner should be passed like key-word arguments. This is means using "=" symbol
between attribute name and content*

Remember to be careful with count of subkeys (in example - "say" and "hello"). Very big count can slow things down. If
it needed - you can use `i18n.get("say-hello", username=...)`
instead of classic sugar-typed dot access method.

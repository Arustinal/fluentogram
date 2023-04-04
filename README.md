# fluentogram

A proper way to use an i18n mechanism with Aiogram3. Using Project Fluent by Mozilla
https://projectfluent.org/fluent/guide/

Short example:

```py
# Somewhere in middleware.Grab language_code from telegram user object, or database, etc.
translator_runner: TranslatorRunner = t_hub.get_translator_by_locale("en")

# In message handler:
async def message_handler(message: Message, ..., i18n: TranslatorRunner):
    ...
    await message.answer(i18n.welcome())
    await message.answer(i18n.greet.by.name(user="Alex")) #aka message.from_user.username
    await message.answer(i18n.shop.success.payment(
        amount=MoneyTransformer(currency="$", amount=Decimal("500")),
        dt=DateTimeTransformer(datetime.now()))

# Going to be like:
    """
    Welcome to the fluent aiogram addon! 
    Hello, Alex! 
    Your money, $500.00, has been sent successfully at Dec 4, 2022.
    """
```

Check [*Examples*](example) folder.

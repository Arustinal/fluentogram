```py
example_ftl_file_content = """
welcome = Welcome to the fluent aiogram addon!
greet-by-name = Hello, { $user }!
shop-success-payment = Your money, { $amount }, has been sent successfully.
"""

# main.py of bot:
example_ftl_file_content = """
welcome = Welcome to the fluent aiogram addon!
greet-by-name = Hello, { $user }!
shop-success-payment = Your money, { $amount }, has been sent successfully at { $dt }.
"""

t_hub = TranslatorHub(
    {"ua": ("ua", "ru", "en"),
     "ru": ("ru", "en"),
     "en": ("en",)},
    translators=[
        FluentTranslator(locale="en",
                         translator=FluentBundle.from_string("en-US", example_ftl_file_content,
                                                             use_isolating=False))],
        FluentTranslator(locale="ru",
                         translator=...)]                                                                 
    root_locale="en",
)

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
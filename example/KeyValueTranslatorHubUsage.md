```py
import asyncio

import nats
from fluent_compiler.bundle import FluentBundle
from nats.js.api import KeyValueConfig, StorageType

from fluentogram import FluentTranslator
from fluentogram import NatsStorage
from fluentogram.src.impl.transator_hubs import KvTranslatorHub

async def main():
    # initialising the NATS connection and JetStream
    nc  = await nats.connect(servers = ["nats://localhost:4222"])
    js = nc.jetstream()
    
    # key/value store creation
    kv_config = KeyValueConfig(
        bucket='my_bucket',
        storage=StorageType.FILE,
    )
    kv = await js.create_key_value(config=kv_config)
    storage = NatsStorage(kv=kv, js=js)

    translator_hub = KvTranslatorHub(
        {
            'ru': ('ru', 'en'),
            'en': ('en',),

        },
        translators=[
            FluentTranslator(locale='en',
                             translator=FluentBundle.from_string(
                                locale='en-US',
                                text='hello = Hello {$name}!')
                             ),
            FluentTranslator(locale='ru',
                             translator=FluentBundle.from_string(
                                 locale='ru',
                                 text='hello = Привет {$name}!')
                             )
        ]
    )
    
    # initialising storage in the translator hub
    await translator_hub.from_storage(kv_storage=storage)

    i18n_ru = translator_hub.get_translator_by_locale(locale='ru')
    i18n_en = translator_hub.get_translator_by_locale(locale='en')
    
    # retrieving texts from passed translators
    print(i18n_ru.hello(name='Александр')) # Привет Александр!
    print(i18n_en.hello(name='Alex')) # Hello Alex!
    
    # creating and updating keys/values
    await translator_hub.put(locale='ru', key='put_key', value='вставленное или обновленное значение №{$number}') # key insertion or replacement
    await translator_hub.create(locale='en', key='create_key', value='create value №{$number}') # only if this key does not exist
    await translator_hub.put(locale='en', mapping_values={
        "mapping_key1": "mapping value №1",
        "mapping_key2": "mapping value №2",
    })
    
    # it may take a few seconds for a listener running in the background to catch and process incoming updates
    await asyncio.sleep(5)
    
    print(i18n_ru.put_key(number=1)) # вставленное или обновленное значение №1
    print(i18n_en.create_key(number=1)) # create value №1
    print(i18n_en.mapping_key1()) # mapping value №1
    print(i18n_en.mapping_key2()) # mapping value №2
    
    # deletion keys/values
    await translator_hub.delete('en', "mapping_key1", "create_key")

if __name__ == '__main__':
    asyncio.run(main())
```
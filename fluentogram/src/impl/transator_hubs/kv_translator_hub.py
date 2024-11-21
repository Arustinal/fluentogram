# coding=utf-8
"""
A Key/Value Translator Hub, using as factory for Translator objects
"""
import asyncio

from typing import Dict, Iterable, Union, Optional, List, Any

from fluent_compiler.bundle import FluentBundle

from fluentogram.exceptions import NotImplementedRootLocaleTranslator
from fluentogram.src.abc import AbstractTranslator
from fluentogram.src.abc.storage import AbstractStorage
from fluentogram.src.abc.translator_hub import AbstractKvTranslatorHub
from fluentogram.src.impl import FluentTranslator
from fluentogram.src.impl.transator_hubs.translator_hub import TranslatorHub

class KvTranslatorHub(TranslatorHub, AbstractKvTranslatorHub):
    def __init__(
            self,
            locales_map: Dict[str, Union[str, Iterable[str]]],
            translators: Optional[List[AbstractTranslator]] = None,
            root_locale: str = "en",
            separator: str = "-"
    ) -> None:
        self.kv_storage = None
        self.messages = None
        if translators is not None:
            super().__init__(locales_map, translators, root_locale, separator)
            return

        self.locales_map = dict(
            zip(
                locales_map.keys(),
                map(
                    lambda lang: tuple([lang]) if isinstance(lang, str) else lang,
                    locales_map.values()
                )
            )
        )
        self.translators = translators
        self.root_locale = root_locale
        self.separator = separator
        self.storage = None
        self.translators_map = None

    async def from_storage(self, kv_storage: AbstractStorage):
        self.kv_storage = kv_storage
        if self.translators is None:
            self.translators = self._create_translators()

            self.storage: Dict[str, AbstractTranslator] = dict(
                zip([translator.locale for translator in self.translators], self.translators)
            )
            if not self.storage.get(self.root_locale):
                raise NotImplementedRootLocaleTranslator(self.root_locale)
            self.translators_map: Dict[str, Iterable[AbstractTranslator]] = self._locales_map_parser(self.locales_map)

        self.messages = self._get_translators_messages()

        asyncio.create_task(self._on_update())

        return self

    async def put(self,
                  locale: str,
                  key: Optional[str] = None,
                  value: Optional[Any] = None,
                  mapping_values: Optional[dict[str, Any]] = None):
        await self.kv_storage.put(locale=locale,
                                  key=key,
                                  value=value,
                                  mapping_values=mapping_values)

    async def create(self,
                     locale: str,
                     key: Optional[str] = None,
                     value: Optional[Any] = None,
                     mapping_values: Optional[dict[str, Any]] = None):
        await self.kv_storage.create(locale,
                                     key,
                                     value,
                                     mapping_values)

    async def delete(self, locale: str, *keys):
        await self.kv_storage.delete(locale, *keys)

    def _create_translators(self) -> list[FluentTranslator]:
        translators = []
        for locale in self.locales_map:
            bundle = FluentBundle(locale=locale, resources=[])
            translators.append(FluentTranslator(locale=locale,
                                                translator=bundle))
        return translators

    def _get_translators_messages(self) -> dict[str, dict]:
        messages = {}
        for translator in self.translators:
            messages[translator.locale] = translator.translator._compiled_messages
        return messages

    async def _on_update(self):
        await asyncio.shield(self.kv_storage.listen(self.messages))
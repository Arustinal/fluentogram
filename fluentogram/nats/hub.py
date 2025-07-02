from __future__ import annotations

import warnings
from typing import Any

from fluentogram.nats.storage import NatsKvStorage
from fluentogram.translator_hub import TranslatorHub


class KvTranslatorHub(TranslatorHub):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "KvTranslatorHub is deprecated and will be removed in 2.0.0 version. "
            "Use TranslatorHub with NatsStorage instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    async def from_storage(self, kv_storage: NatsKvStorage) -> None:
        old_storage = self.storage
        locales_map = old_storage.get_locales_map()
        translators = old_storage.get_all_translators()

        self.storage = kv_storage
        self.storage.add_translators(translators)
        self.storage.set_locales_map(locales_map)

    async def put(
        self,
        locale: str,
        key: str | None = None,
        value: Any | None = None,
        mapping_values: dict[str, Any] | None = None,
    ) -> None:
        if mapping_values is not None:
            for k, v in mapping_values.items():
                await self.put(locale=locale, key=k, value=v)

        if key is not None and value is not None:
            await self.storage.update_translation(
                locale=locale,
                key=key,
                value=value,
            )

    async def create(
        self,
        locale: str,
        key: str,
        value: Any,
        mapping_values: dict[str, Any] | None = None,
    ) -> None:
        await self.put(locale=locale, key=key, value=value, mapping_values=mapping_values)

    async def delete(self, _: str, *__: str) -> None:
        pass

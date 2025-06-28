from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Callable

from nats.aio.msg import Msg
from nats.js import JetStreamContext
from nats.js.kv import KV_DEL, KV_OP, KV_PURGE, KeyValue

from fluentogram.storage.base import BaseStorage

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., bytes]


class NatsKvStorage(BaseStorage):
    def __init__(  # noqa: PLR0913
        self,
        kv: KeyValue,
        js: JetStreamContext,
        separator: str = ".",
        serializer: _JsonDumps = lambda data: json.dumps(data).encode("utf-8"),
        deserializer: _JsonLoads = json.loads,
        consume_timeout: float = 1.0,
    ) -> None:
        self._kv = kv
        self._js = js
        self.separator = separator
        self.serializer = serializer
        self.deserializer = deserializer
        self.consume_timeout = consume_timeout
        super().__init__()

    # NATS-specific methods for async operations
    async def put_translation(
        self,
        locale: str,
        key: str,
        value: Any,
    ) -> None:
        """Put translation to NATS KV store."""
        await self._kv.put(f"{locale}{self.separator}{key}", self.serializer(value))

    async def create_translation(
        self,
        locale: str,
        key: str,
        value: Any,
    ) -> None:
        """Create translation in NATS KV store."""
        await self._kv.create(f"{locale}{self.separator}{key}", self.serializer(value))

    async def delete_translation(self, locale: str, key: str) -> None:
        """Delete translations from NATS KV store."""
        await self._kv.purge(f"{locale}{self.separator}{key}")

    async def listen_for_changes(self) -> None:
        """Listen for changes in NATS KV store and update local storage."""
        stream = await self._js.stream_info(self._kv._stream)  # noqa: SLF001
        stream_name = stream.config.name
        if stream_name is None:
            raise ValueError("Stream name is None")
        subject_name = stream_name.replace("_", self.separator, 1)
        subject = f"${subject_name}.>"
        consumer = await self._js.pull_subscribe(subject=subject, stream=stream_name)
        while True:
            try:
                messages: list[Msg] = await consumer.fetch(50, timeout=self.consume_timeout)
            except TimeoutError:  # noqa: PERF203
                pass
            else:
                await self._update_compiled_messages(messages)

    async def _update_compiled_messages(self, messages: list[Msg]) -> None:
        """Update compiled messages based on NATS KV changes."""
        changes = defaultdict(list)
        for m in messages:
            kind = m.headers.get(KV_OP) if m.headers is not None else None
            *_, locale, key = m.subject.split(self.separator)
            if kind in (KV_DEL, KV_PURGE):
                # Remove translation from local storage
                translator = self._storage.get(locale)
                if translator:
                    print(f"Removing translation: {key}")  # noqa: T201
            else:
                value = self.deserializer(m.data)
                changes[locale].append((key, value))
            await m.ack()
        self._set_new_compiled_messages(changes)

    def _set_new_compiled_messages(self, new_messages: dict[str, list[str]]) -> None:
        """Set new compiled messages for translators."""
        for locale, messages in new_messages.items():
            translator = self._storage.get(locale)
            if translator is None:
                continue

            for key, value in messages:
                translator.update_translation(key, value)

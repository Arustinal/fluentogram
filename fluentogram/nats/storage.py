from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from contextlib import suppress
from typing import Any, Callable

from nats import connect
from nats.aio.msg import Msg
from nats.js import JetStreamContext
from nats.js.api import KeyValueConfig
from nats.js.kv import KV_DEL, KV_OP, KV_PURGE, KeyValue

from fluentogram.storage.base import BaseStorage

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., bytes]

logger = logging.getLogger(__name__)


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
        self._js = js
        self._nc = js._nc  # noqa: SLF001
        self._kv = kv
        self._stream_name = kv._stream  # noqa: SLF001
        self.separator = separator
        self.serializer = serializer
        self.deserializer = deserializer
        self.consume_timeout = consume_timeout
        self._listen_for_changes_task: asyncio.Task | None = None
        self._listen_for_changes_task = asyncio.create_task(self.listen_for_changes())
        self._stop_event = asyncio.Event()
        super().__init__()

    @classmethod
    async def from_servers(
        cls,
        servers: list[str],
        kv_config: KeyValueConfig,
        separator: str = ".",
        serializer: _JsonDumps = lambda data: json.dumps(data).encode("utf-8"),
        deserializer: _JsonLoads = json.loads,
    ) -> NatsKvStorage:
        nc = await connect(servers=servers)
        js = nc.jetstream()
        kv = await js.create_key_value(config=kv_config)
        return cls(kv, js, separator, serializer, deserializer)

    async def update_translation(
        self,
        locale: str,
        key: str,
        value: str,
    ) -> None:
        """Put translation to NATS KV store."""
        await self._kv.put(f"{locale}{self.separator}{key}", self.serializer(value))

    async def _create_consumer(self) -> JetStreamContext.PullSubscription:
        stream = await self._js.stream_info(self._stream_name)
        stream_name = stream.config.name
        if stream_name is None:
            raise ValueError("Stream name is None")
        subject_name = stream_name.replace("_", self.separator, 1)
        subject = f"${subject_name}.>"
        return await self._js.pull_subscribe(subject=subject, stream=stream_name)

    async def _process_messages(self, consumer: JetStreamContext.PullSubscription) -> None:
        """Process messages from the consumer."""
        try:
            messages: list[Msg] = await consumer.fetch(50, timeout=self.consume_timeout)
            if not messages:
                return
            logger.debug("Received %d messages: %s", len(messages), messages)
            await self._update_compiled_messages(messages)
        except TimeoutError:
            pass
        except Exception as e:
            if not self._stop_event.is_set():
                logger.exception("Error in listen_for_changes: %s", exc_info=e)

    async def listen_for_changes(self) -> None:
        """Listen for changes in NATS KV store and update local storage."""
        consumer = await self._create_consumer()
        while not self._stop_event.is_set():
            await self._process_messages(consumer)

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
                    logger.debug("Removing translation: %s", key)
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

    async def close(self) -> None:
        """Close the storage."""
        self._stop_event.set()
        if self._listen_for_changes_task is not None:
            self._listen_for_changes_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._listen_for_changes_task

        await self._nc.close()


NatsStorage = NatsKvStorage  # backward compatibility

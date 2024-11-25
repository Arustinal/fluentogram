# coding=utf-8
"""
NATS-based storage
"""
import asyncio
import json
import sys
from collections import defaultdict
if sys.version_info >= (3, 10):
    from typing import Any, NoReturn, TypeAlias, Optional
else:
    from typing import Any, NoReturn, Optional
    from typing_extensions import TypeAlias

from fluent_compiler.compiler import compile_messages
from fluent_compiler.resource import FtlResource
from nats.aio.msg import Msg
from nats.js import JetStreamContext
from nats.js.kv import KeyValue, KV_OP, KV_DEL, KV_PURGE

from fluentogram.src.abc.storage import AbstractStorage

KeyType: TypeAlias = Optional[str]
ValueType: TypeAlias = Optional[Any]
MappingValuesType: TypeAlias = Optional[dict[KeyType, ValueType]]


class NatsStorage(AbstractStorage):
    def __init__(
            self,
            kv: KeyValue,
            js: JetStreamContext,
            separator: str = '.',
            serializer=lambda data: json.dumps(data).encode('utf-8'),
            deserializer=json.loads
    ):
        self._kv = kv
        self._js = js
        self.separator = separator
        self.messages = None
        self.serializer = serializer
        self.deserializer = deserializer

    async def put(
            self,
            locale: str,
            key: KeyType,
            value: ValueType,
            mapping_values: MappingValuesType
    ):
        await self._interaction(
            func=self._kv.put,
            locale=locale,
            key=key,
            value=value,
            mapping_values=mapping_values
        )

    async def create(
            self,
            locale: str,
            key: KeyType,
            value: ValueType,
            mapping_values: MappingValuesType
    ):
        await self._interaction(
            func=self._kv.create,
            locale=locale,
            key=key,
            value=value,
            mapping_values=mapping_values
        )

    async def delete(self, locale: str, *keys):
        await asyncio.gather(
            *[
                self._kv.purge(f'{locale}{self.separator}{key}')
                for key in keys
            ]
        )

    async def _interaction(
            self,
            func,
            locale: str,
            key: KeyType,
            value: ValueType,
            mapping_values: MappingValuesType
    ):
        if key and value:
            await func(f'{locale}{self.separator}{key}', self.serializer(value))
        if mapping_values:
            await asyncio.gather(
                *[
                    func(f'{locale}{self.separator}{m_key}', self.serializer(m_value))
                    for m_key, m_value in mapping_values.items()
                ]
            )

    async def listen(self, messages: dict[str, dict]) -> NoReturn:
        self.messages = messages
        stream = await self._js.stream_info(self._kv._stream)
        stream_name = stream.config.name
        subject_name = stream_name.replace("_", self.separator, 1)
        subject = f'${subject_name}.>'
        consumer = await self._js.pull_subscribe(subject=subject, stream=stream_name)
        while True:
            try:
                messages: list[Msg] = await consumer.fetch(50)
            except TimeoutError:
                pass
            else:
                await self._update_compiled_messages(messages)

    async def _update_compiled_messages(self, messages: list[Msg]):
        changes = defaultdict(list)
        for m in messages:
            kind = m.headers.get(KV_OP) if m.headers is not None else None
            *args, locale, key = m.subject.split(self.separator)
            if kind in (KV_DEL, KV_PURGE):
                self.messages[locale].pop(key, None)
            else:
                value = self.deserializer(m.data)
                changes[locale].append(f'{key} = {value}')
            await m.ack()
        self._set_new_compiled_messages(changes)

    def _set_new_compiled_messages(self, new_messages: dict[str, list[str]]) -> None:
        for locale, messages in new_messages.items():
            resources = [FtlResource.from_string(message) for message in messages]
            compiled_ftl = compile_messages(locale, resources)
            self.messages[locale].update(compiled_ftl.message_functions)

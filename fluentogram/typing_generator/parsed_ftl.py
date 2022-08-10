from typing import Dict, Iterator

from fluent.syntax import FluentParser
from fluent.syntax.ast import Message, SyntaxNode

from fluentogram.typing_generator.translation_dto import Translation


class ParsedRawFTL:
    def __init__(self, ftl_data: str, parser=FluentParser()) -> None:
        self.parsed_ftl = parser.parse(ftl_data)

    def _filter_elements(self, cls_type) -> Iterator[SyntaxNode]:
        for element in self.parsed_ftl.body:
            if isinstance(element, cls_type):
                yield element

    @staticmethod
    def _construct_translation(chunks: list) -> tuple:
        translation_vars = []
        translation = ""
        for chunk in chunks:
            if content := getattr(chunk, "value", None):
                translation += content
            else:
                chunk_json = chunk.expression.to_json()
                if chunk_json["type"] == "VariableReference":
                    translation_vars.append(chunk_json["id"]["name"])
                    translation += f"{{ ${chunk.expression.id.name} }}"
        return translation_vars, translation

    def get_messages(self) -> Dict[str, Translation]:
        messages = {}
        for message in self._filter_elements(Message):
            translation_vars, value = self._construct_translation(
                message.value.elements
            )
            messages[message.id.name] = Translation(value, args=translation_vars)
        return messages

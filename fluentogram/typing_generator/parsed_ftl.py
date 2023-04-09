from typing import Dict, Tuple, TypeVar, Type
from typing import Iterator

from fluent.syntax import FluentParser
from fluent.syntax.ast import Message
from ordered_set import OrderedSet

from fluentogram.typing_generator.translation_dto import Translation

T = TypeVar("T")


class ParsedRawFTL:
    def __init__(self, ftl_data: str, parser=FluentParser()) -> None:
        self.parsed_ftl = parser.parse(ftl_data)

    def _filter_elements(self, cls_type: Type[T]) -> Iterator[T]:
        for element in self.parsed_ftl.body:
            if isinstance(element, cls_type):
                yield element

    # {'id': {
    #         'span': {'start': 19, 'end': 27, 'type': 'Span'},
    #         'name': 'DATETIME', 'type': 'Identifier'},
    #     'arguments': {'span': {'start': 27, 'end': 34, 'type': 'Span'},
    #                   'positional': [
    #                       {'span': {'start': 28, 'end': 33, 'type': 'Span'},
    #                        'id': {'span': {'start': 29, 'end': 33, 'type': 'Span'},
    #                               'name': 'date', 'type': 'Identifier'},
    #                        'type': 'VariableReference'
    #                        }
    #                   ],
    #     'named': [], 'type': 'CallArguments'}, 'type': 'FunctionReference'}

    @staticmethod
    def _construct_translation(chunks: list) -> Tuple[OrderedSet, str]:
        translation_vars = OrderedSet()
        translation = ""
        for chunk in chunks:
            if content := getattr(chunk, "value", None):
                translation += content
            else:
                chunk_json = chunk.expression.to_json()
                if chunk_json["type"] == "VariableReference":
                    translation_vars.add(chunk_json["id"]["name"])
                    translation += f"{{ ${chunk.expression.id.name} }}"
                elif chunk_json["type"] == "FunctionReference":
                    func_vars = [v for v in chunk_json["arguments"].get("positional", []) if
                                 v["type"] == "VariableReference"]
                    vars_names = [v['id']['name'] for v in func_vars]
                    vars_names_with_prefix = [f"${v}" for v in vars_names]
                    translation += f"{{ {chunk.expression.id.name}({', '.join(vars_names_with_prefix)}) }}"
                    translation_vars.add(vars_names)

        return translation_vars, translation

    def get_messages(self) -> Dict[str, Translation]:
        messages = {}
        for message in self._filter_elements(Message):
            translation_vars, value = self._construct_translation(
                message.value.elements
            )
            messages[message.id.name] = Translation(value, args=translation_vars)
        return messages

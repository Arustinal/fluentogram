from dataclasses import dataclass
from typing import Dict

from fluent.syntax import FluentParser
from fluent.syntax.ast import (
    Message,
    Placeable,
    Literal,
    TextElement,
    VariableReference,
    SelectExpression,
    MessageReference,
    StringLiteral,
    NumberLiteral,
    TermReference,
    FunctionReference,
    InlineExpression,
    NamedArgument,
    Identifier,
)
from ordered_set import OrderedSet

from fluentogram.typing_generator.translation_dto import Translation


@dataclass
class Node:
    value: str
    args: list[str]


class ReferenceNotExists(Exception):
    pass


class ParsedRawFTL:
    def __init__(self, ftl_data: str, parser=FluentParser()) -> None:
        self.parsed_ftl = parser.parse(ftl_data)
        self.nodes: dict[str, Node]

    def _parse_literal(self, obj: Literal) -> Node:
        return Node(value=obj.parse()["value"], args=[])

    def _parse_string_literal(self, obj: StringLiteral) -> Node:
        return self._parse_literal(obj)

    def _parse_number_literal(self, obj: NumberLiteral) -> Node:
        data = obj.parse()
        return Node(value=str(f"{data['value']:.{data['precision']}f}"), args=[])

    def _parse_message_reference(self, obj: MessageReference) -> Node:
        if obj.id.name not in self.nodes:
            raise ReferenceNotExists
        return self.nodes[obj.id.name]

    def _parse_text_element(self, obj: TextElement) -> Node:
        return Node(value=obj.value, args=[])

    def _parse_variable_reference(self, obj: VariableReference) -> Node:
        return Node(value=f"{{ ${obj.id.name} }}", args=[obj.id.name])

    def _parse_named_argument(self, obj: NamedArgument) -> Node:
        if isinstance(obj.value, NumberLiteral):
            value = self._parse_number_literal(obj.value)
        else:  # StringLiteral
            value = self._parse_string_literal(obj.value)
        return Node(value=f"{obj.name.name}: {value.value}", args=[])

    def _parse_function_reference(self, obj: FunctionReference) -> Node:
        named_args = []
        for named_arg in obj.arguments.named:
            named_args.append(self._parse_named_argument(named_arg))
        positionals = []
        for positional in obj.arguments.positional:
            if isinstance(positional, Placeable):
                positionals.append(self._parse_placeable(positional))
            else:  # InlineExpression
                positionals.append(self._parse_inline_expression(positional))

        named_args_string = ", ".join([named_arg.value for named_arg in named_args])
        positional_string = ", ".join([positional.value for positional in positionals])

        positional_args = []
        for positional in positionals:
            positional_args += positional.args

        return Node(
            value=f"{{ {obj.id.name}({positional_string}{',' if named_args_string else ''} {named_args_string}) }}",
            args=positional_args,
        )

    def _parse_inline_expression(self, obj: InlineExpression) -> Node:
        if isinstance(obj, NumberLiteral):
            return self._parse_number_literal(obj)
        elif isinstance(obj, StringLiteral):
            return self._parse_string_literal(obj)
        elif isinstance(obj, MessageReference):
            return self._parse_message_reference(obj)
        elif isinstance(obj, TermReference):
            ...
            # TODO: implementation
        elif isinstance(obj, VariableReference):
            return self._parse_variable_reference(obj)
        elif isinstance(obj, FunctionReference):
            return self._parse_function_reference(obj)
        return Node(value="", args=[])

    def _parse_select_expression(self, obj: SelectExpression) -> Node:
        selector = self._parse_inline_expression(obj.selector)
        value = f"{{ {', '.join([f'${s}' for s in selector.args])} ->"
        args = selector.args

        for variant in obj.variants:
            for element in variant.value.elements:
                if isinstance(element, TextElement):
                    variant_node = self._parse_text_element(element)
                elif isinstance(element, Placeable):
                    variant_node = self._parse_placeable(element)
                else:
                    continue
                if isinstance(variant.key, Identifier):
                    key_name = variant.key.name
                elif isinstance(variant.key, NumberLiteral):
                    key_name = self._parse_number_literal(variant.key).value
                else:
                    continue
                value += f"\n{'*' if variant.default else ''}[{key_name}] {variant_node.value}"
                args += variant_node.args

        value += "\n}"
        return Node(value=value, args=args)

    def _parse_placeable(self, obj: Placeable) -> Node:
        ex = obj.expression
        if isinstance(ex, VariableReference):
            return self._parse_variable_reference(ex)
        elif isinstance(ex, SelectExpression):
            return self._parse_select_expression(ex)
        elif isinstance(ex, InlineExpression):
            return self._parse_inline_expression(ex)
        elif isinstance(ex, Placeable):
            return self._parse_placeable(ex)
        return Node(value="", args=[])

    def _parse_message(self, obj: Message) -> Node:
        nodes: list[Node] = []
        for element in obj.value.elements:
            if isinstance(element, TextElement):
                nodes.append(self._parse_text_element(element))
            elif isinstance(element, Placeable):
                nodes.append(self._parse_placeable(element))
            else:
                continue

        node_value, node_args = "", []
        for sub_node in nodes:
            node_value += sub_node.value
            node_args += sub_node.args
        return Node(value=node_value, args=node_args)

    def _parse_body(self) -> dict[str, Node]:
        self.nodes: dict[str, Node] = {}
        for message in self.parsed_ftl.body:
            if not isinstance(message, Message):
                # TODO: other Entry
                continue
            if message.value is None:
                continue
            try:
                self.nodes[message.id.name] = self._parse_message(message)
            except ReferenceNotExists:
                self.parsed_ftl.body.append(message)
                continue
        return self.nodes

    def get_messages(self) -> Dict[str, Translation]:
        return {
            name: Translation(node.value, args=OrderedSet(node.args))
            for name, node in self._parse_body().items()
        }

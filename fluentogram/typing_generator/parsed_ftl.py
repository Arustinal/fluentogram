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
)
from ordered_set import OrderedSet

from fluentogram.typing_generator.translation_dto import Translation


@dataclass
class Node:
    value: str
    args: list[str]


@dataclass
class Reference:
    name: str


class ParsedRawFTL:
    def __init__(self, ftl_data: str, parser=FluentParser()) -> None:
        self.parsed_ftl = parser.parse(ftl_data)

    def _parse_literal(self, obj: Literal) -> Node:
        return Node(value=obj.parse()["value"], args=[])

    def _parse_string_literal(self, obj: StringLiteral) -> Node:
        return self._parse_literal(obj)

    def _parse_number_literal(self, obj: NumberLiteral) -> Node:
        data = obj.parse()
        return Node(value=str(f"{data['value']:.{data['precision']}f}"), args=[])

    def _parse_message_reference(self, obj: MessageReference) -> Reference:
        return Reference(name=obj.id.name)

    def _parse_text_element(self, obj: TextElement) -> Node:
        return Node(value=obj.value, args=[])

    def _parse_variable_reference(self, obj: VariableReference) -> Node:
        return Node(value=f"{{ ${obj.id.name} }}", args=[obj.id.name])

    def _parse_named_argument(self, obj: NamedArgument) -> Node:
        if isinstance(obj.value, NumberLiteral):
            value = self._parse_number_literal(obj.value)
        elif isinstance(obj.value, StringLiteral):
            value = self._parse_string_literal(obj.value)
        else:
            raise RuntimeError("Wrong NamedArgument type expected")
        return Node(value=f"{obj.name.name}: {value.value}", args=[])

    def _parse_function_reference(self, obj: FunctionReference) -> Node:
        named_args = []
        for named_arg in obj.arguments.named:
            named_args.append(self._parse_named_argument(named_arg))
        positionals = []
        for positional in obj.arguments.positional:
            if isinstance(positional, Placeable):
                positionals.append(self._parse_placeable(positional))
            elif isinstance(positional, InlineExpression):
                positionals.append(self._parse_inline_expression(positional))
            else:
                raise RuntimeError("Wrong CallArguments.positional type expected")

        named_args_string = ", ".join([named_arg.value for named_arg in named_args])
        positional_string = ", ".join([positional.value for positional in positionals])

        positional_args = []
        for positional in positionals:
            positional_args += positional.args

        return Node(
            value=f"{{ {obj.id.name}({positional_string}{',' if named_args_string else ''} {named_args_string}) }}",
            args=positional_args,
        )

    def _parse_inline_expression(
        self, obj: InlineExpression
    ) -> Node | Reference | None:
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
        return None

    def _parse_select_expression(self, obj: SelectExpression) -> Node:
        selector = self._parse_inline_expression(obj.selector)

        variants = []
        for variant in obj.variants:
            for element in variant.value.elements:
                if isinstance(element, TextElement):
                    variant_node = self._parse_text_element(element)
                elif isinstance(element, Placeable):
                    variant_node = self._parse_placeable(element)
                else:
                    continue
                variants.append(
                    {
                        "node": variant_node,
                        "is_default": variant.default,
                        "name": variant.key.name,
                    }
                )

        value = f"{{ {', '.join([f'${s}' for s in selector.args])} }} ->\n"
        value += "\n".join(
            [
                f"{'*' if variant['is_default'] else ''}[{variant['name']}] {variant['node'].value}"
                for variant in variants
            ]
        )
        value += "\n}"
        args = selector.args
        for variant in variants:
            args += variant["node"].args

        return Node(value=value, args=args)

    def _parse_placeable(self, obj: Placeable) -> Node | Reference | None:
        ex = obj.expression
        if isinstance(ex, VariableReference):
            return self._parse_variable_reference(ex)
        elif isinstance(ex, SelectExpression):
            return self._parse_select_expression(ex)
        elif isinstance(ex, InlineExpression):
            return self._parse_inline_expression(ex)
        return None

    def _parse_patterns(self) -> dict[str, list[Node, Reference]]:
        patterns: dict[str, list[Node | Reference]] = {}
        for message in self.parsed_ftl.body:
            if not isinstance(message, Message):
                # TODO: other Entry
                continue
            if message.value is None:
                continue
            for element in message.value.elements:
                if isinstance(element, TextElement):
                    data = self._parse_text_element(element)
                elif isinstance(element, Placeable):
                    data = self._parse_placeable(element)
                else:
                    continue
                if message.id.name not in patterns:
                    patterns[message.id.name] = [data]
                else:
                    patterns[message.id.name].append(data)
        return patterns

    def _split_patterns_by_type(
        self, patterns: dict[str, list[Node, Reference]]
    ) -> tuple[dict[str, list[Node]], dict[str, list[Node, Reference]]]:
        full_nodes_patterns: dict[str, list[Node]] = {}
        mixed_patterns: dict[str, list[Node, Reference]] = {}
        for name, translation in patterns.items():
            is_have_reference = False
            for sub_translation in translation:
                if isinstance(sub_translation, Reference):
                    is_have_reference = True
                    break
            if not is_have_reference:
                full_nodes_patterns[name] = translation
            else:
                mixed_patterns[name] = translation
        return full_nodes_patterns, mixed_patterns

    def _merge_patterns(
        self, patterns: dict[str, list[Node, Reference]]
    ) -> dict[str, Node]:
        merged_patterns: dict[str, Node] = {}

        full_nodes_patterns, mixed_patterns = self._split_patterns_by_type(patterns)

        for name, translation in full_nodes_patterns.items():
            node_value, node_args = "", []
            for sub_translation in translation:
                node_value += sub_translation.value
                node_args += sub_translation.args
            merged_patterns[name] = Node(value=node_value, args=node_args)

        for name, translation in mixed_patterns.items():
            node_value, node_args = "", []
            for sub_translation in translation:
                if isinstance(sub_translation, Node):
                    node_value += sub_translation.value
                    node_args += sub_translation.args
                elif isinstance(sub_translation, Reference):
                    if sub_translation.name not in merged_patterns:
                        continue
                    target_node = merged_patterns[sub_translation.name]
                    node_value += target_node.value
                    node_args += target_node.args
            merged_patterns[name] = Node(value=node_value, args=node_args)

        return merged_patterns

    def get_messages(self) -> Dict[str, Translation]:
        raw_patterns = self._parse_patterns()
        merged_patterns = self._merge_patterns(raw_patterns)
        messages = {}
        for name, translation in merged_patterns.items():
            messages[name] = Translation(
                translation.value, args=OrderedSet(translation.args)
            )
        return messages

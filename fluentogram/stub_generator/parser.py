from __future__ import annotations

import logging
from dataclasses import dataclass, field

from fluent.syntax import FluentParser, ast

logger = logging.getLogger(__name__)


@dataclass
class Message:
    name: str
    result_text: str
    raw_elements: list[ast.TextElement | ast.Placeable]  # Store raw elements for later processing
    placeholders: list[str] = field(default_factory=list)


class Parser:
    def __init__(self) -> None:
        self.messages: dict[str, Message] = {}
        self.terms: dict[str, str] = {}

    def process_term(self, term: ast.Term) -> None:
        for element in term.value.elements:
            if isinstance(element, ast.TextElement):
                self.terms[term.id.name] = element.value
            elif isinstance(element, ast.TermReference):
                self.terms[term.id.name] = self.terms[element.id.name]
            else:
                logger.warning("Unknown element type in term %s: %s", term.id.name, type(element))

    def _parse_variable_reference(self, message_obj: Message, element: ast.VariableReference) -> None:
        if element.id.name not in message_obj.placeholders:
            message_obj.placeholders.append(element.id.name)
        message_obj.result_text += f"{{ ${element.id.name} }}"

    def _parse_term_reference(self, message_obj: Message, element: ast.TermReference) -> None:
        message_obj.result_text += self.terms[element.id.name]

    def _parse_message_reference(self, message_obj: Message, element: ast.MessageReference) -> None:
        if element.id.name in self.messages:
            # Resolve the referenced message recursively
            referenced_message = self.messages[element.id.name]
            if not referenced_message.result_text:
                # If the referenced message hasn't been processed yet, process it now
                self._process_message_elements(referenced_message)
            message_obj.result_text += referenced_message.result_text
            # Add placeholders from referenced message, preserving order and avoiding duplicates
            for placeholder in referenced_message.placeholders:
                if placeholder not in message_obj.placeholders:
                    message_obj.placeholders.append(placeholder)
        else:
            logger.warning("Message reference %s not found", element.id.name)

    def _parse_placeable(self, message_obj: Message, element: ast.Placeable) -> None:
        expression = element.expression
        if isinstance(expression, ast.VariableReference):
            self._parse_variable_reference(message_obj, expression)
        elif isinstance(expression, ast.TermReference):
            self._parse_term_reference(message_obj, expression)
        elif isinstance(expression, ast.SelectExpression):
            self._parse_select_expression(message_obj, expression)
        elif isinstance(expression, ast.FunctionReference):
            self._parse_function_reference(message_obj, expression)
        elif isinstance(expression, ast.MessageReference):
            self._parse_message_reference(message_obj, expression)
        elif isinstance(expression, ast.Placeable):
            self._parse_placeable(message_obj, expression)  # recurse
        else:
            logger.warning("Unknown expression type in placeable %s: %s", message_obj.name, type(expression))

    def _parse_function_reference(self, message_obj: Message, element: ast.FunctionReference) -> None:
        arguments = element.arguments
        for pos_arg in arguments.positional:
            if isinstance(pos_arg, ast.VariableReference):
                self._parse_variable_reference(message_obj, pos_arg)
            else:
                logger.warning(
                    "Unknown positional argument type in function reference %s: %s",
                    message_obj.name,
                    type(pos_arg),
                )

        for named_arg in arguments.named:
            if isinstance(named_arg, ast.VariableReference):
                self._parse_variable_reference(message_obj, named_arg)
            elif isinstance(named_arg, ast.NamedArgument):
                logger.warning(
                    "Skipping named argument '%s' in function reference '%s'",
                    named_arg.name.name,
                    message_obj.name,
                )
            else:
                logger.warning(
                    "Unknown named argument type in function reference %s: %s",
                    message_obj.name,
                    type(named_arg),
                )

    def _parse_select_expression(self, message_obj: Message, element: ast.SelectExpression) -> None:
        """
        Is selector can be many results, so we parse only default variant.
        """
        for variant in element.variants:
            if variant.value is None or not variant.default:
                continue
            for variant_element in variant.value.elements:
                if isinstance(variant_element, ast.TextElement):
                    message_obj.result_text += variant_element.value
                elif isinstance(variant_element, ast.Placeable):
                    self._parse_placeable(message_obj, variant_element)
                else:
                    logger.warning(
                        "Unknown element type in select expression %s: %s",
                        message_obj.name,
                        type(variant_element),
                    )

    def process_message(self, message: ast.Message) -> None:
        # First pass: just collect the message structure
        message_obj = Message(
            name=message.id.name,
            result_text="",
            raw_elements=[],
        )

        if not message.value:
            logger.warning("Message %s has no value", message.id.name)
            self.messages[message.id.name] = message_obj
            return

        # Store raw elements for later processing
        message_obj.raw_elements = message.value.elements
        self.messages[message.id.name] = message_obj

    def _sort_placeholders(self, message_obj: Message) -> None:
        message_obj.placeholders = sorted(message_obj.placeholders)

    def _process_message_elements(self, message_obj: Message) -> None:
        """Process the raw elements of a message to generate result_text and placeholders."""
        # Skip if already processed
        if message_obj.result_text and message_obj.placeholders:
            return

        for element in message_obj.raw_elements:
            if isinstance(element, ast.TextElement):
                message_obj.result_text += element.value
            elif isinstance(element, ast.Placeable):
                self._parse_placeable(message_obj, element)
            else:
                logger.warning("Unknown element type in message %s: %s", message_obj.name, type(element))

        self._sort_placeholders(message_obj)

    def parse(self, resource: ast.Resource) -> dict[str, Message]:
        # First pass: collect all terms and message structures
        for entry in resource.body:
            if isinstance(entry, ast.Term):
                self.process_term(entry)
            elif isinstance(entry, ast.Message):
                self.process_message(entry)

        # Second pass: process all message elements (now all messages are available)
        for message_obj in self.messages.values():
            self._process_message_elements(message_obj)

        return self._get_processed_messages()

    def _get_processed_messages(self) -> dict[str, Message]:
        return {
            message.name: message for message in self.messages.values() if message.result_text or message.placeholders
        }


def get_messages(text: str) -> dict[str, Message]:
    parser = Parser()
    return parser.parse(FluentParser(with_spans=False).parse(text))

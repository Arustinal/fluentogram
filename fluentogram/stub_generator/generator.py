from __future__ import annotations

from pathlib import Path

from fluentogram.stub_generator.parser import Message, get_messages


class Generator:
    def __init__(
        self,
        output_file: str,
        file_path: str | None = None,
        directory: str | None = None,
    ) -> None:
        self.output_file = Path(output_file)
        if self.output_file.suffix != ".pyi":
            raise ValueError("Output file must have .pyi extension")

        if file_path is None and directory is None:
            raise ValueError("Either file_path or directory must be provided")

        self.files = set()  # set of Path objects to skip duplicates
        if file_path:
            self.files.add(Path(file_path))
        if directory:
            self.files.update(Path(directory).glob("*.ftl"))

        self.messages: dict[str, Message] = {}

    def _generate_class_name(self, name: str) -> str:
        """Generate class name from message name."""
        if "-" in name:
            parts = name.split("-")
            return parts[0].title()
        return name.title()

    def _generate_func_signature(self, message: Message, is_method: bool = False, is_call: bool = False) -> str:  # noqa: FBT002
        """Generate function signature for a message."""

        if is_call:
            name = "__call__"
        elif is_method:
            name = message.name.split("-")[1]
        else:
            name = message.name

        formatted_text = f'"""{message.result_text}"""'

        if not message.placeholders:
            return f"    def {name}(self) -> Literal[{formatted_text}]: ..."

        param_list = ", ".join(f"{param}: str" for param in sorted(message.placeholders))
        return f"    def {name}(self, *, {param_list}) -> Literal[{formatted_text}]: ..."

    def _group_messages(
        self,
    ) -> tuple[dict[str, dict[str, Message]], dict[str, Message], dict[str, dict[str, Message]]]:
        grouped_messages = {}
        simple_messages = {}
        conflict_classes = {}

        for name, params in self.messages.items():
            if "-" in name:
                base_name = name.split("-")[0]
                if base_name not in grouped_messages:
                    grouped_messages[base_name] = {}
                grouped_messages[base_name][name] = params
            else:
                simple_messages[name] = params

        # If there is a conflict, move it to conflict_classes and remove from grouped_messages and simple_messages
        for name, messages in list(grouped_messages.items()):
            if name in simple_messages:
                conflict_classes[name] = {}
                conflict_classes[name][name] = simple_messages[name]
                for compound_name, compound_params in messages.items():
                    conflict_classes[name][compound_name] = compound_params
                grouped_messages.pop(name)
                simple_messages.pop(name)

        return grouped_messages, simple_messages, conflict_classes

    def generate(self) -> None:  # noqa: C901
        for file in self.files:
            messages = get_messages(file.read_text())
            self.messages.update(messages)

        # Generate .pyi content
        content = []

        # Group messages by their base name (before dash)
        grouped_messages, simple_messages, conflict_classes = self._group_messages()

        # Generate TranslatorRunner class
        content.append(
            "from typing import Literal\n\nclass TranslatorRunner:\n    def get(self, path: str, **kwargs) -> str: ...",
        )

        # Add simple messages as methods
        content.extend(self._generate_func_signature(message) for message in simple_messages.values())

        # Add grouped messages as attributes
        for base_name in grouped_messages:
            class_name = self._generate_class_name(base_name)
            content.append(f"    {base_name}: {class_name}\n")

        # Add conflict classes as attributes
        for base_name in conflict_classes:
            class_name = self._generate_class_name(base_name)
            content.append(f"    {base_name}: {class_name}\n")

        # Generate classes for grouped messages
        for base_name, messages_dict in grouped_messages.items():
            class_name = self._generate_class_name(base_name)
            content.append(f"class {class_name}:")

            for message in messages_dict.values():
                content.append(self._generate_func_signature(message, is_method=True))
                content.append("")

        # Generate classes for conflict messages
        for base_name, messages_dict in conflict_classes.items():
            class_name = self._generate_class_name(base_name)
            content.append(f"class {class_name}:")

            # Add __call__ for simple key
            if base_name in messages_dict:
                content.append(self._generate_func_signature(messages_dict[base_name], is_call=True))

            # Add methods for compound keys
            for name, message in messages_dict.items():
                if name != base_name:  # Skip simple key, it's already handled as __call__
                    content.append(self._generate_func_signature(message, is_method=True))
            content.append("")

        # Write to file
        self.output_file.write_text("\n".join(content))


def generate(
    output_file: str,
    file_path: str | None = None,
    directory: str | None = None,
) -> None:
    generator = Generator(output_file, file_path, directory)
    generator.generate()

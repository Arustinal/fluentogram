from __future__ import annotations

from pathlib import Path

from fluentogram.exceptions import StubGeneratorKeyConflictError
from fluentogram.stub_generator.parser import get_messages


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

        self.messages = {}

    def _generate_class_name(self, name: str) -> str:
        """Generate class name from message name."""
        if "-" in name:
            parts = name.split("-")
            return parts[0].title()
        return name.title()

    def _generate_method_signature(self, name: str, params: set[str]) -> str:
        """Generate method signature for a message."""
        if not params:
            return f"    def {name}(self) -> str: ..."

        param_list = ", ".join(f"{param}: str" for param in sorted(params))
        return f"    def {name}(self, {param_list}) -> str: ..."

    def _group_messages(self) -> tuple[dict[str, dict[str, set[str]]], dict[str, set[str]]]:
        grouped_messages = {}
        simple_messages = {}
        for name, params in self.messages.items():
            if "-" in name:
                base_name = name.split("-")[0]
                if base_name not in grouped_messages:
                    grouped_messages[base_name] = {}
                grouped_messages[base_name][name] = params
            else:
                simple_messages[name] = params

        return grouped_messages, simple_messages

    def _check_for_conflict(
        self,
        grouped_messages: dict[str, dict[str, set[str]]],
        simple_messages: dict[str, set[str]],
    ) -> None:
        for name, messages in grouped_messages.items():
            if name in simple_messages:
                conflicting_simple = name
                conflicting_grouped = ", ".join(key for key, _ in messages.items())

                raise StubGeneratorKeyConflictError(
                    f"You have conflicting keys in your .ftl file: "  # noqa: EM102
                    f"{conflicting_simple} and {conflicting_grouped}. "
                    f"You can't have a simple key '{conflicting_simple}' "
                    f"and compound keys with prefix '{conflicting_simple}-'.",
                )

    def generate(self) -> None:  # noqa: C901
        for file in self.files:
            messages = get_messages(file.read_text())
            self.messages.update(messages)

        # Generate .pyi content
        content = []

        # Group messages by their base name (before dash)
        grouped_messages, simple_messages = self._group_messages()
        self._check_for_conflict(grouped_messages, simple_messages)

        # Generate TranslatorRunner class
        content.append("class TranslatorRunner:\n    def get(self, path: str, **kwargs) -> str: ...")

        # Add simple messages as methods
        for name, params in simple_messages.items():
            content.append(self._generate_method_signature(name, params))

        # Add grouped messages as attributes
        for base_name in grouped_messages:
            class_name = self._generate_class_name(base_name)
            content.append(f"    {base_name}: {class_name}\n")

        # Generate classes for grouped messages
        for base_name, messages_dict in grouped_messages.items():
            class_name = self._generate_class_name(base_name)
            content.append(f"class {class_name}:")

            for name, params in messages_dict.items():
                method_name = name.split("-")[1]  # Get part after dash
                content.append(self._generate_method_signature(method_name, params))
                content.append("")

        # Write to file
        self.output_file.write_text("\n".join(content))


def generate(output_file: str, file_path: str | None = None, directory: str | None = None) -> None:
    generator = Generator(output_file, file_path, directory)
    generator.generate()

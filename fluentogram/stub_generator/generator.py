from __future__ import annotations

from pathlib import Path

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

    def _group_messages(
        self,
    ) -> tuple[dict[str, dict[str, set[str]]], dict[str, set[str]], dict[str, dict[str, set[str]]]]:
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
        content.append("class TranslatorRunner:\n    def get(self, path: str, **kwargs) -> str: ...")

        # Add simple messages as methods
        for name, params in simple_messages.items():
            content.append(self._generate_method_signature(name, params))

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

            for name, params in messages_dict.items():
                method_name = name.split("-")[1]  # Get part after dash
                content.append(self._generate_method_signature(method_name, params))
                content.append("")

        # Generate classes for conflict messages
        for base_name, messages_dict in conflict_classes.items():
            class_name = self._generate_class_name(base_name)
            content.append(f"class {class_name}:")

            # Add __call__ for simple key
            if base_name in messages_dict:
                content.append("    def __call__(self) -> str: ...")

            # Add methods for compound keys
            for name, params in messages_dict.items():
                if name != base_name:  # Skip simple key, it's already handled as __call__
                    method_name = name.split("-")[1]  # Get part after dash
                    content.append(self._generate_method_signature(method_name, params))
            content.append("")

        # Write to file
        self.output_file.write_text("\n".join(content))


def generate(output_file: str, file_path: str | None = None, directory: str | None = None) -> None:
    generator = Generator(output_file, file_path, directory)
    generator.generate()

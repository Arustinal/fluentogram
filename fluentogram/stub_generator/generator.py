from __future__ import annotations

from pathlib import Path

from fluentogram.stub_generator.parser import Message, get_messages
from fluentogram.stub_generator.stubs import generate_stubs
from fluentogram.stub_generator.tree import build_tree


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

    def generate(self) -> None:
        for file in self.files:
            messages = get_messages(file.read_text())
            self.messages.update(messages)

        tree = build_tree(self.messages)
        content = generate_stubs(tree)
        self.output_file.write_text(content)


def generate(
    output_file: str,
    file_path: str | None = None,
    directory: str | None = None,
) -> None:
    generator = Generator(output_file, file_path, directory)
    generator.generate()

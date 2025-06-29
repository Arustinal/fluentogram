import tempfile
from pathlib import Path

import pytest

from fluentogram.exceptions import StubGeneratorKeyConflictError
from fluentogram.stub_generator.generator import generate


def test_conflict_error() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    with pytest.raises(StubGeneratorKeyConflictError):
        generate(output_path, file_path="tests/assets/broken.ftl")


def test_correctly_generated_stub_for_simple_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/simple.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "def hello(self) -> str: ..." in content
    assert "def button(self) -> str: ..." in content


def test_correctly_generated_stub() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/test.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "def get(self, path: str, **kwargs) -> str: ..." in content
    assert "def hello(self) -> str: ..." in content
    assert "def button(self) -> str: ..." in content
    assert "def multiline(self) -> str: ..." in content
    assert "def welcome(self, name: str) -> str: ..." in content
    assert "def button(self) -> str: ..." in content
    assert "def multiline(self) -> str: ..." in content
    assert "def score(self, points: str) -> str: ..." in content
    assert "def escaped(self, notAVar: str) -> str: ..." in content
    assert "def about(self) -> str: ..." in content
    assert "class Email:" in content
    assert "def status(self, unreadCount: str) -> str: ..." in content
    assert "class Task:" in content
    assert "def state(self, state: str) -> str: ..." in content
    assert "class Formatted:" in content
    assert "def date(self, date: str) -> str: ..." in content
    assert "class Outer:" in content
    assert "class Inner:" in content
    assert "class Complex:" in content
    assert "def multiline(self) -> str: ..." in content
    assert "def welcome(self, name: str) -> str: ..." in content
    assert "def button(self) -> str: ..." in content
    assert "def multiline(self) -> str: ..." in content
    assert "def score(self, points: str) -> str: ..." in content

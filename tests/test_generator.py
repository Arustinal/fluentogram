import tempfile
from pathlib import Path

from fluentogram.stub_generator.generator import generate


def test_correctly_generated_stub_for_simple_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/simple.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert 'def hello(self) -> Literal["""Hello, world!"""]: ...' in content
    assert 'def button(self) -> Literal["""Button"""]: ...' in content


def test_generator_if_conflict() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/conflict.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "class Button" in content
    assert 'def __call__(self) -> Literal["""Button"""]: ...' in content
    assert 'def text(self) -> Literal["""Button text"""]: ...' in content


def test_correctly_generated_stub() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/test.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "def get(self, path: str, **kwargs) -> str: ..." in content
    assert 'def hello(self) -> Literal["""Hello, world!"""]: ...' in content
    assert 'def multiline(self) -> Literal["""This is a multiline message.' in content
    assert 'def welcome(self, *, name: str) -> Literal["""Hello, { $name }!"""]: ...' in content
    assert "class Email:" in content
    assert (
        'def status(self, *, unreadCount: str) -> Literal["""You have { $unreadCount } new emails."""]: ...' in content
    )
    assert 'def greeting(self) -> Literal["""Hello, world! This is a phrase with another message."""]: ...' in content
    assert "class Task:" in content
    assert 'def state(self) -> Literal["""Unknown state"""]: ...' in content
    assert "class Formatted:" in content
    assert 'def date(self, *, date: str) -> Literal["""Today: { $date }"""]: ...' in content
    assert 'def score(self, *, points: str) -> Literal["""You scored { $points } points"""]: ...' in content
    assert "class Outer:" in content
    assert 'def message(self) -> Literal["""Attachment: This is a nested message."""]: ...' in content
    assert "class Inner:" in content
    assert 'def message(self) -> Literal["""This is a nested message.This is a nested message."""]: ...' in content
    assert 'def escaped(self, *, notAVar: str) -> Literal["""This is not a variable: { $notAVar }"""]: ...' in content
    assert 'def about(self) -> Literal["""Information about Application X"""]: ...' in content
    assert "class Complex:" in content
    assert (
        '''def message(self, *, date: str, name: str, unreadCount: str) -> Literal["""Welcome, { $name }!
Today { $date }.
You have { $unreadCount } new emails.
Thank you for using Application X!"""]: ...'''
        in content
    )

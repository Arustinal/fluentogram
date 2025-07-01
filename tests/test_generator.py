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
    assert 'def hello() -> Literal["""Hello, world!"""]: ...' in content
    assert 'def button() -> Literal["""Button"""]: ...' in content


def test_generator_if_conflict() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/conflict.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "class Button" in content
    assert 'def __call__() -> Literal["""Button"""]: ...' in content
    assert 'def text() -> Literal["""Button text"""]: ...' in content


def test_correctly_generated_stub() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/test.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "def get(self, path: str, **kwargs: PossibleValue) -> str: ..." in content
    assert 'def hello() -> Literal["""Hello, world!"""]: ...' in content
    assert 'def multiline() -> Literal["""This is a multiline message.' in content
    assert 'def welcome(*, name: PossibleValue) -> Literal["""Hello, { $name }!"""]: ...' in content
    assert "class Email:" in content
    assert (
        'def status(*, unreadCount: PossibleValue) -> Literal["""You have { $unreadCount } new emails."""]: ...'
        in content
    )
    assert 'def greeting() -> Literal["""Hello, world! This is a phrase with another message."""]: ...' in content
    assert "class Task:" in content
    assert 'def state() -> Literal["""Unknown state"""]: ...' in content
    assert "class Formatted:" in content
    assert 'def date(*, date: PossibleValue) -> Literal["""Today: { $date }"""]: ...' in content
    assert 'def score(*, points: PossibleValue) -> Literal["""You scored { $points } points"""]: ...' in content
    assert "class Outer:" in content
    assert 'def message() -> Literal["""Attachment: This is a nested message."""]: ...' in content
    assert "class Inner:" in content
    assert 'def message() -> Literal["""This is a nested message.This is a nested message."""]: ...' in content
    assert (
        'def escaped(*, notAVar: PossibleValue) -> Literal["""This is not a variable: { $notAVar }"""]: ...' in content
    )
    assert 'def about() -> Literal["""Information about Application X"""]: ...' in content
    assert "class Complex:" in content
    assert (
        '''def message(*, date: PossibleValue, name: PossibleValue, unreadCount: PossibleValue) -> Literal["""Welcome, { $name }!
Today { $date }.
You have { $unreadCount } new emails.
Thank you for using Application X!"""]: ...'''
        in content
    )
    assert 'def shielded() -> Literal["""&#34;Must be shielded&#34;"""]: ...' in content


def test_generator_if_conflict_in_prefix() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pyi", delete=False) as tmp_file:
        output_path = tmp_file.name

    generate(output_path, file_path="tests/assets/conflict_in_prefix.ftl")

    assert Path(output_path).exists()
    content = Path(output_path).read_text()

    assert "class TranslatorRunner:" in content
    assert "class FirstUnknown" in content
    assert "class AnotherUnknown" in content
    assert 'def error() -> Literal["""first-unknown-error"""]: ...' in content
    assert 'def error() -> Literal["""another-unknown-error"""]: ...' in content

# coding=utf-8
import unittest
from fluentogram.typing_generator import ParsedRawFTL, Tree, Stubs


class StubGeneration(unittest.TestCase):
    def test_stub_generation(self):
        raw = ParsedRawFTL(EXAMPLE_FTL_CONTEXT)
        messages = raw.get_messages()
        tree = Tree(messages)
        stubs = Stubs(tree)

        assert stubs.echo() == EXPECTED_OUTPUT


EXAMPLE_FTL_CONTEXT = """
welcome = Welcome to the fluent aiogram addon!
greet-by-name = Hello, { $user }... You name is { $user }, isn't it?
shop-success-payment = Your money, { $amount }, has been sent successfully at { $dt }.
"""

EXPECTED_OUTPUT = '''from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    greet: Greet
    shop: Shop

    @staticmethod
    def welcome() -> Literal["""Welcome to the fluent aiogram addon!"""]: ...


class Greet:
    by: GreetBy


class GreetBy:
    @staticmethod
    def name(*, user) -> Literal["""Hello, { $user }... You name is { $user }, isn&#39;t it?"""]: ...


class Shop:
    success: ShopSuccess


class ShopSuccess:
    @staticmethod
    def payment(*, amount, dt) -> Literal["""Your money, { $amount }, has been sent successfully at { $dt }."""]: ...

'''

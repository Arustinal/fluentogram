# coding=utf-8
import unittest

from fluentogram.typing_generator import ParsedRawFTL, Tree, Stubs


class StubGeneration(unittest.TestCase):
    DEFAULT_STUB_TEXT = """from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    """

    def _gen_stub_text(self, raw_text):
        raw = ParsedRawFTL(raw_text)
        messages = raw.get_messages()
        tree = Tree(messages)
        stubs = Stubs(tree)
        return stubs.echo()

    def test_text_element(self):
        self.assertEquals(
            self._gen_stub_text("welcome = Welcome to the fluent aiogram addon!"),
            self.DEFAULT_STUB_TEXT
            + '''
    @staticmethod
    def welcome() -> Literal["""Welcome to the fluent aiogram addon!"""]: ...

''',
        )

    def test_variable_reference(self):
        self.assertEquals(
            self._gen_stub_text(
                "greet-by-name = Hello, { $user }... You name is { $user }, isn't it?"
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    greet: Greet


class Greet:
    by: GreetBy


class GreetBy:
    @staticmethod
    def name(*, user) -> Literal["""Hello, { $user }... You name is { $user }, isn&#39;t it?"""]: ...

''',
        )

    def test_variable_reference_with_two_args(self):
        self.assertEquals(
            self._gen_stub_text(
                "shop-success-payment = Your money, { $amount }, has been sent successfully at { $dt }."
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    shop: Shop


class Shop:
    success: ShopSuccess


class ShopSuccess:
    @staticmethod
    def payment(*, amount, dt) -> Literal["""Your money, { $amount }, has been sent successfully at { $dt }."""]: ...

''',
        )

    def test_selector(self):
        self.assertEquals(
            self._gen_stub_text(
                """test-bool_indicator = { $is_true ->
                    [one] ✅
                    *[other] ❌
                } """
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    test: Test


class Test:
    @staticmethod
    def bool_indicator(*, is_true) -> Literal["""{ $is_true -&gt;
[one] ✅
*[other] ❌
}"""]: ...

''',
        )

    def test_selector_num_key(self):
        self.assertEquals(
            self._gen_stub_text(
                """test-bool_indicator = { $is_true ->
                    [0] ✅
                    *[other] ❌
                } """
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    test: Test


class Test:
    @staticmethod
    def bool_indicator(*, is_true) -> Literal["""{ $is_true -&gt;
[0] ✅
*[other] ❌
}"""]: ...

''',
        )

    def test_recursion(self):
        self.assertEquals(
            self._gen_stub_text(
                """recursion = { $is_true ->
[one] one
*[other] Recursion { $is_true -> 
            [one] one
            *[other] Recursion { $is_true -> 
            [one] one
            *[other] Recursion
            }
            }
}"""
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    @staticmethod
    def recursion(*, is_true) -> Literal["""{ $is_true -&gt;
[one] one
*[other] Recursion 
*[other] { $is_true -&gt;
[one] one
*[other] Recursion 
*[other] { $is_true -&gt;
[one] one
*[other] Recursion
}
}
}"""]: ...

''',
        )

    def test_function_reference(self):
        self.assertEquals(
            self._gen_stub_text("test-number = { NUMBER($num, useGrouping: 0) }"),
            self.DEFAULT_STUB_TEXT
            + '''
    test: Test


class Test:
    @staticmethod
    def number(*, num) -> Literal["""{ NUMBER({ $num }, useGrouping: 0) }"""]: ...

''',
        )

    def test_message_reference_to_text(self):
        self.assertEquals(
            self._gen_stub_text(
                """simple = text
ref = { simple }
            """
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    @staticmethod
    def simple() -> Literal["""text"""]: ...

    @staticmethod
    def ref() -> Literal["""text"""]: ...

''',
        )

    def test_message_reference_to_var(self):
        self.assertEquals(
            self._gen_stub_text(
                """var = { $name }
ref = { var }
            """
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    @staticmethod
    def var(*, name) -> Literal["""{ $name }"""]: ...

    @staticmethod
    def ref(*, name) -> Literal["""{ $name }"""]: ...

''',
        )

    def test_message_reference_in_selector(self):
        self.assertEquals(
            self._gen_stub_text(
                """foo = { $var ->
[test] { test }
*[any] any text
}
test = { $is_true ->
[one] true
*[other] false
}
"""
            ),
            self.DEFAULT_STUB_TEXT
            + '''
    @staticmethod
    def test(*, is_true) -> Literal["""{ $is_true -&gt;
[one] true
*[other] false
}"""]: ...

    @staticmethod
    def foo(*, var, is_true) -> Literal["""{ $var -&gt;
[test] { $is_true -&gt;
[one] true
*[other] false
}
*[any] any text
}"""]: ...

''',
        )

from __future__ import annotations

from collections.abc import Iterable

from jinja2 import Environment, Template


def create_jinja_env() -> Environment:
    """Create Jinja2 environment with custom filters"""
    env = Environment(autoescape=True)

    def camelcase(value: str) -> str:
        """Convert dash/underscore separated string to CamelCase"""
        return "".join(word.capitalize() for word in value.replace("_", "-").split("-"))

    env.filters["camelcase"] = camelcase
    return env


jinja_env = create_jinja_env()


class RenderAble:
    render_pattern: Template

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def render(self) -> str:
        return self.render_pattern.render(**self.kwargs)


class Import(RenderAble):
    render_pattern = jinja_env.from_string("from typing import Literal")


class Method(RenderAble):
    render_pattern = jinja_env.from_string(
        '    @staticmethod\n    def {{ method_name }}({{ args }}) -> Literal["""{{ result_text }}"""]: ...',
    )

    def __init__(
        self,
        method_name: str,
        result_text: str,
        args: Iterable[str] | None = None,
    ) -> None:
        formatted_args = "*, " + ", ".join(f"{arg}: PossibleValue" for arg in args) if args else ""
        super().__init__(result_text=result_text, args=formatted_args)
        self.kwargs["method_name"] = method_name

    def render(self) -> str:
        return super().render() + "\n"


class InternalMethod(Method):
    def __init__(self, result_text: str, args: Iterable[str] | None = None) -> None:
        super().__init__(method_name="__call__", result_text=result_text, args=args)


class ClassRef(RenderAble):
    render_pattern = jinja_env.from_string(
        "    {{ var_name }}: {{ var_full_name | camelcase }}",
    )

    def __init__(self, var_name: str, var_full_name: str | None = None) -> None:
        super().__init__(
            var_name=var_name,
            var_full_name=var_full_name or var_name,
        )

    def render(self) -> str:
        return super().render() + "\n"


class Class(RenderAble):
    render_pattern = jinja_env.from_string("\nclass {{ class_name | camelcase }}:")

    def __init__(self, class_name: str) -> None:
        super().__init__()
        self.class_name = class_name
        self.class_refs: list[ClassRef] = []
        self.methods: list[Method] = []

    def render(self) -> str:
        text = self.render_pattern.render(class_name=self.class_name) + "\n"
        for class_ref in self.class_refs:
            text += class_ref.render()
        if self.class_refs:
            text += "\n"
        for method in self.methods:
            text += method.render()
        return text.rstrip() + "\n"

    def add_class_ref(self, class_ref: ClassRef) -> None:
        self.class_refs.append(class_ref)

    def add_method(self, method: Method) -> None:
        self.methods.append(method)


class Runner(Class):
    render_pattern = jinja_env.from_string(
        """from decimal import Decimal
from typing import Literal

from fluent_compiler.types import FluentType
from typing_extensions import TypeAlias

PossibleValue: TypeAlias = str | int | float | Decimal | bool | FluentType

class {{ class_name }}:
    def get(self, path: str, **kwargs: PossibleValue) -> str: ...""",
    )

    def __init__(self, knots: list[Class], name: str = "TranslatorRunner") -> None:
        super().__init__(name)
        self.knots = knots

    def render(self) -> str:
        text = super().render()
        for knot in self.knots:
            text += knot.render()
        return text

    def add_knot(self, knot: Class) -> None:
        self.knots.append(knot)

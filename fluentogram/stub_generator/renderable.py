from __future__ import annotations

from collections.abc import Iterable

from jinja2 import Environment, Template


def create_jinja_env() -> Environment:
    """Create Jinja2 environment with custom filters"""
    env = Environment(autoescape=True)

    def title(value: str) -> str:
        """Convert string to title case"""
        return value.title()

    env.filters["title"] = title
    return env


jinja_env = create_jinja_env()


class RenderAble:
    render_pattern: Template

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def render(self) -> str:
        return self.render_pattern.render(**self.kwargs) + "\n"


class Import(RenderAble):
    render_pattern = jinja_env.from_string("from typing import Literal")


class Method(RenderAble):
    render_pattern = jinja_env.from_string(
        '    @staticmethod\n    def {{ method_name }}({{ args }}) -> Literal["""{{ translation }}"""]: ...',
    )

    def __init__(
        self,
        method_name: str,
        translation: str,
        args: Iterable[str] | None = None,
    ) -> None:
        formatted_args = "*, " + ", ".join(args) if args else ""
        super().__init__(translation=translation, args=formatted_args)
        self.kwargs["method_name"] = method_name


class InternalMethod(Method):
    def __init__(self, translation: str, args: Iterable[str] | None = None) -> None:
        super().__init__(method_name="__call__", translation=translation, args=args)


class ClassRef(RenderAble):
    render_pattern = jinja_env.from_string(
        "    {{ var_name }}: {{ var_full_name | title }}",
    )

    def __init__(self, var_name: str, var_full_name: str | None = None) -> None:
        super().__init__(
            var_name=var_name,
            var_full_name=var_full_name or var_name,
        )


class Class(RenderAble):
    render_pattern = jinja_env.from_string("\nclass {{ class_name | title }}:\n")

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
            text += method.render() + "\n"
        return text

    def add_class_ref(self, class_ref: ClassRef) -> None:
        self.class_refs.append(class_ref)

    def add_method(self, method: Method) -> None:
        self.methods.append(method)


class Runner(Class):
    render_pattern = jinja_env.from_string(
        "\nclass {{ class_name }}:\n    def get(self, path: str, **kwargs) -> str: ...\n    ",
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

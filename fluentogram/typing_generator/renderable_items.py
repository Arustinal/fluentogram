# coding=utf-8
from typing import Optional, List

try:
    from jinja2 import Template
except ModuleNotFoundError:
    raise ModuleNotFoundError("You should install Jinja2 package to use cli tools")


class RenderAble:
    render_pattern: Template

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def render(self) -> str:
        return self.render_pattern.render(**self.kwargs) + "\n"


class Import(RenderAble):
    render_pattern = Template("from typing import Literal", autoescape=True)


class Method(RenderAble):
    render_pattern = Template(
        "    @staticmethod\n"
        '    def {{ method_name }}({{ args }}) -> Literal["""{{ translation }}"""]: ...',
        autoescape=True,
    )

    def __init__(
            self, method_name: str, translation: str, args: Optional[list] = None
    ) -> None:
        if args:
            formatted_args = "*, " + ", ".join(args)
        else:
            formatted_args = ""
        super().__init__(translation=translation, args=formatted_args)
        self.kwargs["method_name"] = method_name


class InternalMethod(Method):
    def __init__(self, translation: str, args: Optional[list] = None) -> None:
        super().__init__(method_name="__call__", translation=translation, args=args)


class Var(RenderAble):
    render_pattern = Template(
        "    {{ var_name }}: {{ var_full_name }}", autoescape=True
    )

    def __init__(self, var_name: str, var_full_name: str = None) -> None:
        super().__init__(
            var_name=var_name,
            var_full_name=var_name if not var_full_name else var_full_name,
        )


class Knot(RenderAble):
    render_pattern = Template("\nclass {{ class_name }}:\n", autoescape=True)

    def __init__(self, class_name: str) -> None:
        super().__init__()
        self.class_name = class_name
        self.variables: List[Var] = []
        self.methods: List[Method] = []

    def render(self) -> str:
        text = self.render_pattern.render(class_name=self.class_name) + "\n"
        for var in self.variables:
            text += var.render()
        if self.variables:
            text += "\n"
        for method in self.methods:
            text += method.render() + "\n"
        return text

    def add_var(self, var: Var) -> None:
        self.variables.append(var)

    def add_method(self, method: Method) -> None:
        self.methods.append(method)


class Runner(Knot):
    render_pattern = Template(
        "\nclass {{ class_name }}:\n    def get(self, path: str, **kwargs) -> str: ...\n    ",
        autoescape=True,
    )

    def __init__(self, name: str = "TranslatorRunner") -> None:
        super().__init__(name)

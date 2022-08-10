from typing import Iterator

from fluentogram.typing_generator.renderable_items import (
    Var,
    Knot,
    InternalMethod,
    Method,
    Runner,
)
from fluentogram.typing_generator.tree import Tree


class Stubs:
    def __init__(self, tree: Tree, root: str = "TranslatorRunner") -> None:
        self.root = root
        self.nodes = tree.elements
        self.content: str = "from typing import Literal\n\n    "
        for stub in self._gen_stubs():
            self.content += stub

    def _gen_stubs(self) -> Iterator[str]:
        for path, node in self.nodes.items():
            if node.is_leaf:
                continue
            if node.path:
                knot = Knot(node.path)
            else:
                knot = Runner(self.root)
            if node.children:
                if node.value:
                    knot.add_method(
                        InternalMethod(node.value, args=node.translation_vars)
                    )
                for name, sub_node in node.children.items():
                    if sub_node.is_leaf:
                        if sub_node.value:
                            knot.add_method(
                                Method(
                                    name, sub_node.value, args=sub_node.translation_vars
                                )
                            )
                    else:
                        knot.add_var(Var(name, sub_node.path))
            yield knot.render()

    def to_file(self, file_name: str) -> None:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(self.content)

    def echo(self) -> str:
        return self.content

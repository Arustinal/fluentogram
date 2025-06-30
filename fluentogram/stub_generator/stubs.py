from fluentogram.stub_generator.renderable import (
    InternalMethod,
    Knot,
    Method,
    Runner,
    Var,
)
from fluentogram.stub_generator.tree import Tree


def generate_stubs(tree: Tree) -> str:
    content = "from typing import Literal\n"
    for node in tree.elements.values():
        if node.is_leaf:
            continue
        knot = Knot(node.path) if node.path else Runner()
        if node.children:
            if node.value:
                knot.add_method(
                    InternalMethod(node.value, args=node.placeholders),
                )
            for name, sub_node in node.children.items():
                if sub_node.is_leaf:
                    if sub_node.value:
                        knot.add_method(
                            Method(
                                name,
                                sub_node.value,
                                args=sub_node.placeholders,
                            ),
                        )
                else:
                    knot.add_var(Var(name, sub_node.path))
        content += knot.render()
    return content

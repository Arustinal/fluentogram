from fluentogram.stub_generator.renderable import (
    Class,
    ClassRef,
    InternalMethod,
    Method,
    Runner,
)
from fluentogram.stub_generator.tree import TreeNode


def _process_node(node: TreeNode, runner: Runner) -> Class:
    """Recursively processes tree node and creates corresponding class"""
    knot = Class(node.name)

    # If node has value (translation), add method __call__
    if node.value is not None:
        knot.add_method(
            InternalMethod(node.value, args=node.placeholders),
        )

    # Process child nodes
    for name, sub_node in node.children.items():
        if sub_node.is_leaf:
            # If child node is leaf with value, add method
            if sub_node.value is not None:
                knot.add_method(
                    Method(
                        name,
                        sub_node.value,
                        args=sub_node.placeholders,
                    ),
                )
        else:
            # If child node is not leaf, create class reference
            sub_class = _process_node(sub_node, runner)
            runner.add_knot(sub_class)
            knot.add_class_ref(ClassRef(name, sub_class.class_name))

    return knot


def generate_stubs(tree: TreeNode) -> str:
    content = "from typing import Literal\n"
    runner = Runner(knots=[])

    # Process root nodes
    for node in tree.children.values():
        if node.is_leaf:
            # If root node is leaf, add it as method to Runner
            if node.value is not None:
                runner.add_method(
                    Method(
                        node.name,
                        node.value,
                        args=node.placeholders,
                    ),
                )
        else:
            # If root node is not leaf, create class
            knot = _process_node(node, runner)
            runner.add_class_ref(ClassRef(node.name, knot.class_name))
            runner.add_knot(knot)

    content += runner.render()
    return content

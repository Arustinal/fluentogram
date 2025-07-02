from fluentogram.stub_generator.templates import (
    Class,
    ClassRef,
    InternalMethod,
    Method,
    Runner,
)
from fluentogram.stub_generator.tree import TreeNode

PYTHON_RESERVED_KEYWORDS = {
    "class",
    "def",
    "if",
    "else",
    "elif",
    "not",
    "in",
    "is",
    "and",
    "or",
    "as",
    "assert",
    "break",
    "continue",
    "return",
    "yield",
    "from",
    "import",
    "pass",
    "raise",
    "try",
    "except",
    "finally",
    "with",
    "while",
    "for",
    "lambda",
    "match",
    "async",
    "await",
    "True",
    "False",
    "None",
    "self",
    "super",
}


def _is_reserved_keyword(name: str) -> bool:
    return name in PYTHON_RESERVED_KEYWORDS


def _is_valid_python_name(name: str) -> bool:
    return not name.isdigit() and not _is_reserved_keyword(name)


def _process_node(node: TreeNode, runner: Runner, parent_path: str = "") -> Class:
    """Recursively processes tree node and creates corresponding class"""
    # Create unique class name by combining parent path with node name
    current_path = f"{parent_path}-{node.name}" if parent_path else node.name

    knot = Class(current_path)

    # If node has value (translation), add method __call__
    if node.value is not None:
        knot.add_method(
            InternalMethod(result_text=node.value, args=node.placeholders),
        )

    # Process child nodes
    for name, sub_node in node.children.items():
        if sub_node.is_leaf:
            # If child node is leaf with value, add method
            if sub_node.value is not None:
                if not _is_valid_python_name(name):
                    print(f"{name} is not a valid Python name")
                    continue
                knot.add_method(
                    Method(
                        method_name=name,
                        result_text=sub_node.value,
                        args=sub_node.placeholders,
                    ),
                )
        else:
            if not _is_valid_python_name(name):
                print(f"{name} is not a valid Python name")
                continue
            # If child node is not leaf, create class reference
            sub_class = _process_node(sub_node, runner, current_path)
            runner.add_knot(sub_class)
            knot.add_class_ref(ClassRef(name, sub_class.class_name))

    return knot


def generate_stubs(tree: TreeNode) -> str:
    content = ""
    runner = Runner(knots=[])

    # Process root nodes
    for node in tree.children.values():
        if node.is_leaf:
            # If root node is leaf, add it as method to Runner
            if node.value is not None:
                runner.add_method(
                    Method(
                        method_name=node.name,
                        result_text=node.value,
                        args=node.placeholders,
                    ),
                )
        else:
            # If root node is not leaf, create class
            knot = _process_node(node, runner)
            if not _is_valid_python_name(node.name):
                print(f"{node.name} is not a valid Python name")
                continue
            runner.add_class_ref(ClassRef(node.name, knot.class_name))
            runner.add_knot(knot)

    content += runner.render()
    return content

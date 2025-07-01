from __future__ import annotations

from dataclasses import dataclass, field

from fluentogram.stub_generator.parser import Message


@dataclass
class TreeNode:
    """Translation tree node"""

    name: str
    value: str | None = None
    placeholders: list[str] = field(default_factory=list)
    children: dict[str, TreeNode] = field(default_factory=dict)

    @property
    def is_leaf(self) -> bool:
        """Is node a leaf (has no children)"""
        return not self.children

    @property
    def has_value(self) -> bool:
        """Does node have value (translation)"""
        return self.value is not None


def _build_node(key: str, message: Message, root: TreeNode, separator: str = "-") -> TreeNode:
    parts = key.split(separator)

    # Start with root
    current_node = root

    # Process all parts of the path, except the last one
    for part in parts[:-1]:
        # If child node does not exist, create it
        if part not in current_node.children:
            current_node.children[part] = TreeNode(name=part)
        current_node = current_node.children[part]

    # Last part is the node name with value
    final_name = parts[-1]

    # Create or update final node
    if final_name not in current_node.children:
        current_node.children[final_name] = TreeNode(
            name=final_name,
            value=message.result_text,
            placeholders=message.placeholders,
        )
    else:
        # If node already exists, update its value
        existing_node = current_node.children[final_name]
        existing_node.value = message.result_text
        existing_node.placeholders = message.placeholders

    return current_node


def build_tree(messages: dict[str, Message], separator: str = "-") -> TreeNode:
    root = TreeNode(name="root")
    for key, message in messages.items():
        _build_node(key, message, root, separator)
    return root

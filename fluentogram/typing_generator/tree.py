from dataclasses import dataclass
from typing import Optional

from ordered_set import OrderedSet

from fluentogram.typing_generator.translation_dto import Translation


@dataclass
class TreeNode:
    path: str
    children: dict[str, "TreeNode"]
    name: str
    value: Optional[str] = None
    translation_vars: Optional[OrderedSet] = None

    @property
    def is_leaf(self) -> bool:
        if not self.children:
            return True
        return False


class Tree:
    def __init__(
            self,
            ftl_syntax: dict[str, Translation],
            separator: str = "-",
            safe_separator: str = "",
    ) -> None:
        self.safe_separator = safe_separator
        self.ftl_syntax = ftl_syntax
        self.separator = separator
        self.elements: dict[tuple[str, ...], TreeNode] = {}
        for path, translation in ftl_syntax.items():
            *point_path, name = path.split("-")
            point_path.insert(0, "")
            self._build(tuple(point_path), name, translation)

    def path_to_str(self, path: tuple) -> str:
        clean_path = map(lambda s: s[0].capitalize() + s[1:], filter(lambda x: x, path))
        return self.safe_separator.join(clean_path)

    def _build(self, path: tuple[str, ...], name: str, value=None) -> None:
        own_class_def = TreeNode(
            path=self.path_to_str(path + (name,)),
            name=name,
            value=value.text if value else "",
            children={},
            translation_vars=value.args if value else OrderedSet(),
        )

        if path:
            if path not in self.elements:
                self._build(path[:-1], path[-1])

            self.elements[path].children[name] = own_class_def

        self.elements.setdefault(path + (name,), own_class_def)

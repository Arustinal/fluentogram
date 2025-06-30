from __future__ import annotations

from dataclasses import dataclass, field

from fluentogram.stub_generator.parser import Message


@dataclass
class TreeNode:
    path: str
    children: dict[str, TreeNode]
    name: str
    value: str | None = None
    placeholders: list[str] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children


class Tree:
    def __init__(
        self,
        ftl_syntax: dict[str, Message],
        separator: str = "-",
        safe_separator: str = "",
    ) -> None:
        self.safe_separator = safe_separator
        self.ftl_syntax = ftl_syntax
        self.separator = separator
        self.elements: dict[tuple[str, ...], TreeNode] = {}

        for path, translation in ftl_syntax.items():
            *point_path, name = path.split(self.separator)
            point_path.insert(0, "")
            self._build(tuple(point_path), name, translation)

    def path_to_str(self, path: tuple[str, ...]) -> str:
        clean_path = (s[0].capitalize() + s[1:] for s in filter(lambda x: x, path))
        return self.safe_separator.join(clean_path)

    def _build(self, path: tuple[str, ...], name: str, value: Message | None = None) -> None:
        own_class_def = TreeNode(
            path=self.path_to_str((*path, name)),
            name=name,
            value=value.result_text if value else "",
            children={},
            placeholders=value.placeholders if value else [],
        )

        if path:
            if path not in self.elements:
                self._build(path[:-1], path[-1])

            self.elements[path].children[name] = own_class_def

        self.elements.setdefault((*path, name), own_class_def)

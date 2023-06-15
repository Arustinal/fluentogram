from dataclasses import dataclass

from ordered_set import OrderedSet


@dataclass
class Translation:
    text: str
    args: OrderedSet

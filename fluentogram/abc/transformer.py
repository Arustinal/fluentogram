"""An AbstractDataTransformer object, using to transform any data before being passed to translator directly."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractDataTransformer(ABC):
    """These transformers inspired by Functions of Project Fluent by Mozilla.
    Of course, it's a simple function, like a

    def function(money: Union[int, float], **kwargs) -> str: ...

    which result passes through translator, into engine itself, like a Fluent or anything else.
    """

    @abstractmethod
    def __new__(cls, data: Any, **kwargs: Any) -> Any:
        """Using incoming data, create an object representation of these data for your translator via all needed
        parameters using kwargs
        """
        raise NotImplementedError

from abc import ABC, abstractmethod
from collections.abc import Iterator

from .messages import Message
from .response import Response


class Model(ABC):
    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        tools: list[dict],
        system: str | None = None,
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    def stream(
        self,
        messages: list[Message],
        tools: list[dict],
        system: str | None = None,
    ) -> Iterator[str]:
        raise NotImplementedError

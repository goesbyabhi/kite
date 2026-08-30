from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @property
    def requires_confirmation(self) -> bool:
        return False

    def confirmation_message(
        self,
        arguments: dict[str, Any],
    ) -> str:
        return f"Kite wants to use {self.name}."

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def schema(self) -> dict:
        raise NotImplementedError

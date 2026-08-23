from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]
    thought_signature: str | None = None


@dataclass
class Response:
    text: str | None = None
    tool_calls: list[ToolCall] | None = None

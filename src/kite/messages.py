from dataclasses import dataclass
from typing import Any

from .response import ToolCall


@dataclass
class Message:
    role: str
    content: str | None = None

    tool_calls: list[ToolCall] | None = None

    tool_call_id: str | None = None
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None

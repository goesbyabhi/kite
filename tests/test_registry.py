from typing import Any

import pytest

from kite.tools.base import Tool
from kite.tools.registry import ToolRegistry


class FakeTool(Tool):
    @property
    def name(self) -> str:
        return "fake"

    @property
    def description(self) -> str:
        return "A fake tool for testing."

    def execute(self, arguments: dict[str, Any]) -> str:
        return f"Hello {arguments['name']}"

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
            },
        }


def test_registry_get_tool():
    tool = FakeTool()
    registry = ToolRegistry([tool])

    assert registry.get("fake") is tool


def test_registry_unknown_tool():
    registry = ToolRegistry([FakeTool()])

    with pytest.raises(ValueError, match="Unknown tool"):
        registry.get("missing")


def test_registry_execute():
    registry = ToolRegistry([FakeTool()])

    result = registry.execute(
        "fake",
        {"name": "Abhishek"},
    )

    assert result == "Hello Abhishek"


def test_registry_definitions():
    registry = ToolRegistry([FakeTool()])

    definitions = registry.definitions()

    assert len(definitions) == 1
    assert definitions[0]["name"] == "fake"

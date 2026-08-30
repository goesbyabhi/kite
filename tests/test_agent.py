from typing import Any

from kite.agent import Agent
from kite.messages import Message
from kite.response import Response, ToolCall
from kite.tools.base import Tool
from kite.tools.registry import ToolRegistry


class FakeTool(Tool):
    @property
    def name(self) -> str:
        return "fake"

    @property
    def description(self) -> str:
        return "A fake tool."

    def execute(self, arguments: dict[str, Any]) -> str:
        return f"result: {arguments['value']}"

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string"},
                },
                "required": ["value"],
            },
        }


class ConfirmedTool(FakeTool):
    @property
    def requires_confirmation(self) -> bool:
        return True


class FakeModel:
    def __init__(self, responses: list[Response]):
        self.responses = iter(responses)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict],
        system: str | None = None,
    ) -> Response:
        return next(self.responses)


def test_agent_returns_text():
    model = FakeModel(
        [
            Response(text="Hello Abhishek"),
        ]
    )

    agent = Agent(
        model,
        ToolRegistry([]),
    )

    result = agent.run("Say hello")

    assert result == "Hello Abhishek"


def test_agent_executes_tool():
    model = FakeModel(
        [
            Response(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="fake",
                        arguments={"value": "hello"},
                    )
                ]
            ),
            Response(text="Done"),
        ]
    )

    agent = Agent(
        model,
        ToolRegistry([FakeTool()]),
    )

    result = agent.run("Use the fake tool")

    assert result == "Done"


def test_agent_keeps_conversation_memory():
    model = FakeModel(
        [
            Response(text="First response"),
            Response(text="Second response"),
        ]
    )

    agent = Agent(
        model,
        ToolRegistry([]),
    )

    assert agent.run("First") == "First response"
    assert agent.run("Second") == "Second response"

    assert len(agent.messages) == 4
    assert agent.messages[0].content == "First"
    assert agent.messages[2].content == "Second"


def test_agent_stops_at_max_steps():
    tool_call = ToolCall(
        id="1",
        name="fake",
        arguments={"value": "hello"},
    )

    model = FakeModel(
        [
            Response(tool_calls=[tool_call]),
            Response(tool_calls=[tool_call]),
            Response(tool_calls=[tool_call]),
        ]
    )

    agent = Agent(
        model,
        ToolRegistry([FakeTool()]),
    )

    try:
        agent.run("Keep going", max_steps=2)
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        assert "maximum steps" in str(e)


def test_agent_confirmation_allowed(monkeypatch):
    model = FakeModel(
        [
            Response(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="fake",
                        arguments={"value": "hello"},
                    )
                ]
            ),
            Response(text="Done"),
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: "y")

    agent = Agent(
        model,
        ToolRegistry([ConfirmedTool()]),
    )

    result = agent.run("Use the tool")

    assert result == "Done"


def test_agent_confirmation_denied(monkeypatch):
    model = FakeModel(
        [
            Response(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="fake",
                        arguments={"value": "hello"},
                    )
                ]
            )
        ]
    )

    monkeypatch.setattr("builtins.input", lambda _: "n")

    agent = Agent(
        model,
        ToolRegistry([ConfirmedTool()]),
    )

    result = agent.run("Use the tool")

    assert result == "Operation cancelled by user."

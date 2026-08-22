from .base import Tool


class ToolRegistry:
    def __init__(self, tools: list[Tool]):
        self._tools = {
            tool.name: tool
            for tool in tools
        }

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(
                f"Unknown tool: {name}"
            )

    def definitions(self) -> list[dict]:
        return [
            tool.schema()
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        arguments: dict,
    ) -> str:
        tool = self.get(name)
        return tool.execute(arguments)

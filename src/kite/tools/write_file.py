from typing import Any

from ..workspace import Workspace
from .base import Tool

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}


class WriteFile(Tool):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write text content to a file in the project workspace."

    @property
    def requires_confirmation(self) -> bool:
        return True

    def confirmation_message(
        self,
        arguments: dict[str, Any],
    ) -> str:
        return f"Kite wants to write:\n  {arguments['path']}"

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content to write.",
                    },
                },
                "required": ["path", "content"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        path = self.workspace.resolve(arguments["path"])

        if path.name in SENSITIVE_FILES:
            raise PermissionError(f"Access denied: {path.name} is a sensitive file.")

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            arguments["content"],
            encoding="utf-8",
        )

        return f"Wrote {path.relative_to(self.workspace.root)}"

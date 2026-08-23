from typing import Any

from ..workspace import Workspace
from .base import Tool

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}


class ReadFile(Tool):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a text file."

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read.",
                    }
                },
                "required": ["path"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        path = self.workspace.resolve(arguments["path"])

        if path.name in SENSITIVE_FILES:
            raise PermissionError(f"Access denied: {path.name} is a sensitive file.")

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        return path.read_text(encoding="utf-8")

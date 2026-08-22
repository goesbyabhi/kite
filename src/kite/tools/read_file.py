from pathlib import Path
from typing import Any

from .base import Tool


class ReadFile(Tool):
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
        path = Path(arguments["path"])

        if not path.is_file():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        return path.read_text(encoding="utf-8")

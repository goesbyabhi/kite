from typing import Any

from ..workspace import Workspace
from .base import Tool

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}


class EditFile(Tool):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Replace an exact piece of text in a file in the project workspace."

    @property
    def requires_confirmation(self) -> bool:
        return True

    def confirmation_message(
        self,
        arguments: dict[str, Any],
    ) -> str:
        return f"Kite wants to edit:\n  {arguments['path']}"

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to edit.",
                    },
                    "old_text": {
                        "type": "string",
                        "description": (
                            "Exact text currently present in the file "
                            "that should be replaced."
                        ),
                    },
                    "new_text": {
                        "type": "string",
                        "description": "Text that should replace old_text.",
                    },
                },
                "required": ["path", "old_text", "new_text"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        path = self.workspace.resolve(arguments["path"])

        if path.name in SENSITIVE_FILES:
            raise PermissionError(f"Access denied: {path.name} is a sensitive file.")

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text(encoding="utf-8")

        old_text = arguments["old_text"]
        new_text = arguments["new_text"]

        count = content.count(old_text)

        if count == 0:
            raise ValueError("The specified old_text was not found in the file.")

        if count > 1:
            raise ValueError(
                "The specified old_text appears multiple times. "
                "The edit must match exactly one location."
            )

        updated = content.replace(old_text, new_text, 1)

        path.write_text(
            updated,
            encoding="utf-8",
        )

        return f"Edited {path.relative_to(self.workspace.root)}"

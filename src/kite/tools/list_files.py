from pathlib import Path
from typing import Any

from ..workspace import Workspace
from .base import Tool

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}

IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}


class ListFiles(Tool):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return (
            "List files and directories in a project. "
            "Hidden and generated directories are excluded."
        )

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory to inspect. Use '.' for the current project."
                        ),
                    }
                },
                "required": ["path"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        path = self.workspace.resolve(arguments["path"])

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        lines = []

        self._walk(path, path, lines)

        return "\n".join(lines)

    def _walk(
        self,
        root: Path,
        current: Path,
        lines: list[str],
    ) -> None:
        try:
            entries = sorted(
                current.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except PermissionError:
            return

        for entry in entries:
            if entry.name in IGNORED_FILES:
                continue
            if entry.is_dir() and entry.name in IGNORED_DIRECTORIES:
                continue

            relative = entry.relative_to(root)

            if entry.is_dir():
                lines.append(f"{relative}/")
                self._walk(root, entry, lines)
            else:
                lines.append(str(relative))

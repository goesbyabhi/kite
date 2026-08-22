from pathlib import Path
from typing import Any

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


class Search(Tool):
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "Search project files for a text pattern. "
            "Returns matching file paths, line numbers, and lines."
        )

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text to search for.",
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "Directory or file to search. "
                            "Use '.' for the project."
                        ),
                    },
                },
                "required": ["query", "path"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        query = arguments["query"]
        path = Path(arguments["path"])

        if not path.exists():
            raise FileNotFoundError(
                f"Path not found: {path}"
            )

        results: list[str] = []

        if path.is_file():
            self._search_file(
                path,
                query,
                results,
            )
        else:
            self._search_directory(
                path,
                query,
                results,
            )

        if not results:
            return "No matches found."

        return "\n".join(results)

    def _search_directory(
        self,
        root: Path,
        query: str,
        results: list[str],
    ) -> None:
        for current, directories, files in root.walk():

            directories[:] = [
                directory
                for directory in directories
                if directory not in IGNORED_DIRECTORIES
            ]

            for filename in files:
                if filename in IGNORED_FILES:
                    continue

                self._search_file(
                    current / filename,
                    query,
                    results,
                )

    def _search_file(
        self,
        path: Path,
        query: str,
        results: list[str],
    ) -> None:
        try:
            text = path.read_text(
                encoding="utf-8"
            )
        except (
            UnicodeDecodeError,
            PermissionError,
            OSError,
        ):
            return

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):
            if query.lower() in line.lower():
                results.append(
                    f"{path}:{line_number}: {line.strip()}"
                )

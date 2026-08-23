from pathlib import Path


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def resolve(self, path: str) -> Path:
        candidate = (self.root / path).resolve()

        try:
            candidate.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"Path is outside the workspace: {path}")

        return candidate

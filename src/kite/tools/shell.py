import subprocess
from typing import Any

from ..workspace import Workspace
from .base import Tool


class Shell(Tool):
    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return (
            "Execute a PowerShell command in the project workspace. "
            "Use this for running tests, linters, builds, and other "
            "project commands."
        )

    @property
    def requires_confirmation(self) -> bool:
        return True

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": ("PowerShell command to execute."),
                    }
                },
                "required": ["command"],
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        command = arguments["command"]

        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    command,
                ],
                cwd=self.workspace.root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds."

        output = []

        if result.stdout:
            output.append(result.stdout.rstrip())

        if result.stderr:
            output.append(result.stderr.rstrip())

        output.append(f"Process exited with code {result.returncode}.")

        return "\n".join(output)

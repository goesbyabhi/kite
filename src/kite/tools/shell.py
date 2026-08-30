import subprocess
from typing import Any

from ..workspace import Workspace
from .base import Tool

MAX_OUTPUT = 20_000


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
            "Use this for running tests, linters, builds, programs, "
            "and other project commands. "
            "A command with exit code 0 succeeded, even if stdout is empty. "
            "Do not repeat a successful command."
        )

    @property
    def requires_confirmation(self) -> bool:
        return True

    def confirmation_message(
        self,
        arguments: dict[str, Any],
    ) -> str:
        return f"Kite wants to execute:\n  {arguments['command']}"

    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "PowerShell command to execute.",
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
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds."

        stdout = self._truncate(result.stdout)
        stderr = self._truncate(result.stderr)

        return (
            f"Exit code: {result.returncode}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )

    @staticmethod
    def _truncate(output: str) -> str:
        output = output.rstrip()

        if len(output) <= MAX_OUTPUT:
            return output

        omitted = len(output) - MAX_OUTPUT

        return (
            output[:MAX_OUTPUT]
            + "\n\n"
            f"[output truncated: {omitted} characters omitted]"
        )

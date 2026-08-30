from pathlib import Path

from kite.tools.shell import Shell
from kite.workspace import Workspace


def test_shell_captures_stdout(tmp_path: Path):
    tool = Shell(Workspace(tmp_path))

    result = tool.execute(
        {"command": 'Write-Output "hello"'}
    )

    assert "Exit code: 0" in result
    assert "hello" in result


def test_shell_captures_stderr(tmp_path: Path):
    tool = Shell(Workspace(tmp_path))

    result = tool.execute(
        {
            "command": (
                '[Console]::Error.WriteLine("something went wrong")'
            )
        }
    )

    assert "Exit code: 0" in result
    assert "something went wrong" in result


def test_shell_reports_nonzero_exit(tmp_path: Path):
    tool = Shell(Workspace(tmp_path))

    result = tool.execute(
        {"command": "exit 1"}
    )

    assert "Exit code: 1" in result


def test_shell_runs_in_workspace(tmp_path: Path):
    tool = Shell(Workspace(tmp_path))

    result = tool.execute(
        {"command": "(Get-Location).Path"}
    )

    assert str(tmp_path) in result


def test_shell_timeout(tmp_path: Path):
    tool = Shell(Workspace(tmp_path), timeout=1)

    result = tool.execute(
        {"command": "Start-Sleep -Seconds 3"}
    )

    assert result == "Command timed out after 30 seconds."

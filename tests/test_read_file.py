from pathlib import Path

import pytest

from kite.tools.read_file import ReadFile
from kite.workspace import Workspace


def test_read_file(tmp_path: Path):
    file = tmp_path / "hello.txt"
    file.write_text("hello abhishek")

    tool = ReadFile(Workspace(tmp_path))

    result = tool.execute({"path": "hello.txt"})

    assert result == "hello abhishek"


def test_read_file_blocks_env(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("SECRET=123")

    tool = ReadFile(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        tool.execute({"path": ".env"})


def test_read_file_missing_file(tmp_path: Path):
    tool = ReadFile(Workspace(tmp_path))

    with pytest.raises(FileNotFoundError):
        tool.execute({"path": "missing.txt"})

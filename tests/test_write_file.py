from pathlib import Path

import pytest

from kite.tools.write_file import WriteFile
from kite.workspace import Workspace


def test_write_file(tmp_path: Path):
    tool = WriteFile(Workspace(tmp_path))

    result = tool.execute(
        {
            "path": "hello.py",
            "content": 'print("hello")',
        }
    )

    assert (tmp_path / "hello.py").read_text() == 'print("hello")'
    assert result == "Wrote hello.py"


def test_write_file_creates_parent_directories(tmp_path: Path):
    tool = WriteFile(Workspace(tmp_path))

    tool.execute(
        {
            "path": "src/hello.py",
            "content": "print('hello')",
        }
    )

    assert (tmp_path / "src/hello.py").exists()


def test_write_file_blocks_env(tmp_path: Path):
    tool = WriteFile(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        tool.execute(
            {
                "path": ".env",
                "content": "SECRET=123",
            }
        )


def test_write_file_blocks_path_escape(tmp_path: Path):
    tool = WriteFile(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        tool.execute(
            {
                "path": "../secret.txt",
                "content": "secret",
            }
        )

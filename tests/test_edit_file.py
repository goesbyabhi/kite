from pathlib import Path

import pytest

from kite.tools.edit_file import EditFile
from kite.workspace import Workspace


def test_edit_file(tmp_path: Path):
    file = tmp_path / "hello.py"
    file.write_text('return "hello"')

    tool = EditFile(Workspace(tmp_path))

    result = tool.execute(
        {
            "path": "hello.py",
            "old_text": '"hello"',
            "new_text": '"hello abhishek"',
        }
    )

    assert file.read_text() == 'return "hello abhishek"'
    assert result == "Edited hello.py"


def test_edit_file_text_not_found(tmp_path: Path):
    file = tmp_path / "hello.py"
    file.write_text('return "hello"')

    tool = EditFile(Workspace(tmp_path))

    with pytest.raises(ValueError):
        tool.execute(
            {
                "path": "hello.py",
                "old_text": '"banana"',
                "new_text": '"apple"',
            }
        )


def test_edit_file_missing_file(tmp_path: Path):
    tool = EditFile(Workspace(tmp_path))

    with pytest.raises(FileNotFoundError):
        tool.execute(
            {
                "path": "missing.py",
                "old_text": "hello",
                "new_text": "bye",
            }
        )


def test_edit_file_blocks_env(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("SECRET=123")

    tool = EditFile(Workspace(tmp_path))

    with pytest.raises(PermissionError):
        tool.execute(
            {
                "path": ".env",
                "old_text": "SECRET=123",
                "new_text": "SECRET=456",
            }
        )

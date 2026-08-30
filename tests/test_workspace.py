from pathlib import Path

import pytest

from kite.workspace import Workspace


def test_resolve_normal_path(tmp_path: Path):
    workspace = Workspace(tmp_path)

    result = workspace.resolve("hello.py")

    assert result == tmp_path / "hello.py"


def test_resolve_blocks_path_escape(tmp_path: Path):
    workspace = Workspace(tmp_path)

    with pytest.raises(PermissionError):
        workspace.resolve("../secret.txt")


def test_resolve_blocks_absolute_path_escape(tmp_path: Path):
    workspace = Workspace(tmp_path)

    outside = tmp_path.parent / "secret.txt"

    with pytest.raises(PermissionError):
        workspace.resolve(str(outside))

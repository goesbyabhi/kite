from ..workspace import Workspace
from .base import Tool
from .edit_file import EditFile
from .list_files import ListFiles
from .read_file import ReadFile
from .search import Search
from .shell import Shell
from .write_file import WriteFile


def default_tools(workspace: Workspace) -> list[Tool]:
    return [
        ReadFile(workspace),
        ListFiles(workspace),
        Search(workspace),
        Shell(workspace),
        WriteFile(workspace),
        EditFile(workspace),
    ]

from pathlib import Path

from dotenv import load_dotenv

from .agent import Agent
from .gemini import Gemini
from .tools.edit_file import EditFile
from .tools.list_files import ListFiles
from .tools.read_file import ReadFile
from .tools.registry import ToolRegistry
from .tools.search import Search
from .tools.shell import Shell
from .tools.write_file import WriteFile
from .workspace import Workspace


def main():
    load_dotenv()

    workspace = Workspace(Path.cwd())

    model = Gemini("gemini-3.5-flash-lite")

    tools = ToolRegistry(
        [
            ReadFile(workspace),
            ListFiles(workspace),
            Search(workspace),
            Shell(workspace),
            WriteFile(workspace),
            EditFile(workspace),
        ]
    )

    agent = Agent(model, tools)

    print("kite 🪁")

    while True:
        try:
            print()
            prompt = input("> ")
        except EOFError, KeyboardInterrupt:
            print()
            break

        if prompt == "/quit":
            break

        if not prompt.strip():
            continue

        try:
            response = agent.run(prompt)
            print(response)

        except Exception as e:  # noqa: BLE001
            print(f"error: {e}")


if __name__ == "__main__":
    main()

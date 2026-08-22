from dotenv import load_dotenv

from .agent import Agent
from .gemini import Gemini
from .tools.registry import ToolRegistry
from .tools.read_file import ReadFile
from .tools.list_files import ListFiles
from .tools.search import Search


def main():
    load_dotenv()

    model = Gemini("gemini-3.5-flash-lite")

    tools = ToolRegistry([
        ReadFile(),
        ListFiles(),
        Search(),
    ])

    agent = Agent(model, tools)

    print("kite 🪁")

    while True:
        try:
            prompt = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if prompt == "/quit":
            break

        if not prompt.strip():
            continue

        try:
            response = agent.run(prompt)
            print(response)

        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    main()

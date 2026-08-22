from dotenv import load_dotenv

from .agent import Agent
from .gemini import Gemini
from .tools.read_file import ReadFile
from .tools.registry import ToolRegistry


def main():
    load_dotenv()

    model = Gemini("gemini-3.6-flash")

    tools = ToolRegistry([
        ReadFile(),
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

from .messages import Message
from .models import Model
from .tools.registry import ToolRegistry

SYSTEM_PROMPT = """
You are Kite, a minimal coding agent.

You work inside the user's project workspace.

Use the available tools to inspect and modify the codebase when necessary.

Rules:
- Do not guess about files or code. Inspect them when needed.
- Use search to locate relevant code.
- Use read_file to inspect files.
- Use list_files to understand project structure.
- Use shell to run project commands, tests, linters, and builds.
- Prefer project-local tools through uv when available.
- Run commands from the project workspace.
- Never attempt to access sensitive files.
- Stay concise and technical.
""".strip()

class Agent:
    def __init__(
        self,
        model: Model,
        tools: ToolRegistry,
    ):
        self.model = model
        self.tools = tools

    def run(
        self,
        prompt: str,
        max_steps: int = 10,
    ) -> str:

        messages = [
            Message(
                role="user",
                content=prompt,
            )
        ]

        for _ in range(max_steps):
            response = self.model.complete(
                messages,
                tools=self.tools.definitions(),
                system=SYSTEM_PROMPT,
            )

            # Keep the model response in the conversation.
            messages.append(
                Message(
                    role="assistant",
                    content=response.text,
                    tool_calls=response.tool_calls,
                )
            )

            # No tool call = we're done.
            if not response.tool_calls:
                return response.text or ""

            # Execute every requested tool.
            for call in response.tool_calls:
                tool = self.tools.get(call.name)

                if tool.requires_confirmation:
                    command = call.arguments.get("command", "")

                    answer = input(
                        f"\nKite wants to execute:\n  {command}\nAllow? [y/N] "
                    )

                    if answer.lower() != "y":
                        result = "User denied execution."

                        messages.append(
                            Message(
                                role="tool",
                                content=result,
                                tool_call_id=call.id,
                                tool_name=call.name,
                            )
                        )

                        continue
                try:
                    result = self.tools.execute(
                        call.name,
                        call.arguments,
                    )

                except Exception as e:  # noqa: BLE001
                    result = f"Tool error: {e}"

                messages.append(
                    Message(
                        role="tool",
                        content=result,
                        tool_call_id=call.id,
                        tool_name=call.name,
                    )
                )

        raise RuntimeError(f"Agent exceeded maximum steps ({max_steps})")

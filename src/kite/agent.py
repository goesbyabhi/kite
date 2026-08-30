import json

from .messages import Message
from .models import Model
from .tools.registry import ToolRegistry

SYSTEM_PROMPT = """
You are Kite, a minimal coding agent.

You work inside the user's project workspace.

Use the available tools to inspect and modify the codebase when necessary.

General rules:
- Do not guess about files or code. Inspect them when needed.
- Use the minimum number of tool calls necessary to complete the user's request.
- Do not perform additional actions after the user's request has been satisfied.
- Treat tool errors as authoritative.
- Do not repeat the same tool call with identical arguments after it fails.
- A successful tool call is sufficient evidence that the requested operation completed.
- Do not perform verification unless the user requests it or verification is necessary to determine whether the task succeeded.

Tool usage rules:
- Use read_file or search to inspect code when necessary.
- Use write_file when creating or completely replacing a file.
- Use edit_file for targeted modifications to existing files.
- Use shell for commands, tests, linters, builds, and running programs.
- Do not run tests, linters, builds, or formatters unless the user asks for them or they are necessary to complete the task.
- Do not retry a successful shell command with another command.
- If a shell command fails, inspect the error before deciding whether a retry is appropriate.
- When the user asks to run a program, execute it once using the most direct appropriate command.
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

        executed_tools: set[tuple[str, str]] = set()

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

                tool_key = (
                    call.name,
                    json.dumps(
                        call.arguments,
                        sort_keys=True,
                    ),
                )

                if tool_key in executed_tools:
                    result = (
                        "This exact tool call was already executed successfully "
                        "during this task. Do not repeat it. "
                        "Continue from the existing result."
                    )

                    messages.append(
                        Message(
                            role="tool",
                            content=result,
                            tool_call_id=call.id,
                            tool_name=call.name,
                        )
                    )

                    continue

                if tool.requires_confirmation:
                    answer = input(
                        f"\n{tool.confirmation_message(call.arguments)}\nAllow? [y/N] "
                    )

                    if answer.lower() != "y":
                        return "Operation cancelled by user."

                try:
                    result = self.tools.execute(
                        call.name,
                        call.arguments,
                    )
                    executed_tools.add(tool_key)

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

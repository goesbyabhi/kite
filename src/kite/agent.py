from .messages import Message
from .models import Model
from .tools.registry import ToolRegistry


class Agent:
    def __init__(
        self,
        model: Model,
        tools: ToolRegistry,
    ):
        self.model = model
        self.tools = tools

    def run(self, prompt: str) -> str:

        messages = [
            Message(
                role="user",
                content=prompt,
            )
        ]

        while True:

            response = self.model.complete(
                messages,
                tools=self.tools.definitions(),
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

                try:
                    result = self.tools.execute(
                        call.name,
                        call.arguments,
                    )

                except Exception as e:
                    result = f"Tool error: {e}"

                messages.append(
                    Message(
                        role="tool",
                        content=result,
                        tool_call_id=call.id,
                        tool_name=call.name,
                    )
                )

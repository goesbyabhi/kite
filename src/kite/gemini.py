import os
from typing import Any

import httpx

from .messages import Message
from .models import Model
from .response import Response, ToolCall


class Gemini(Model):
    def __init__(self, model: str):
        self.model = model

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to your .env file."
            )

        self.api_key = api_key

    def complete(
        self,
        messages: list[Message],
        tools: list[dict],
    ) -> Response:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:generateContent"
        )

        response = httpx.post(
            url,
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "contents": self._build_contents(messages),
                **self._build_tools(tools),
            },
            timeout=60,
        )

        if response.is_error:
            raise RuntimeError(
                f"Gemini API Error ({response.status_code}): "
                f"{response.text}"
            )

        return self._parse_response(response.json())

    def _build_contents(
        self,
        messages: list[Message],
    ) -> list[dict[str, Any]]:

        contents = []

        for message in messages:

            if message.role == "user":
                contents.append({
                    "role": "user",
                    "parts": [
                        {"text": message.content}
                    ],
                })

            elif message.role == "assistant":
                parts = []

                if message.content:
                    parts.append({
                        "text": message.content
                    })

                if message.tool_calls:
                    for call in message.tool_calls:
                        part = {
                                 "functionCall": {
                                     "name": call.name,
                                     "args": call.arguments,
                             }
                         }

                        if call.thought_signature:
                             part["thoughtSignature"] = call.thought_signature

                        parts.append(part)

                contents.append({
                    "role": "model",
                    "parts": parts,
                })

            elif message.role == "tool":
                contents.append({
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": message.tool_name,
                                    "response": {
                                        "result": message.content,
                                    },
                                }
                            }
                        ],
                    })

        return contents

    def _build_tools(
        self,
        tools: list[dict],
    ) -> dict:

        if not tools:
            return {}

        return {
            "tools": [
                {
                    "functionDeclarations": tools
                }
            ]
        }

    def _parse_response(
        self,
        data: dict,
    ) -> Response:

        parts = (
            data["candidates"][0]
            ["content"]["parts"]
        )

        text_parts = []
        tool_calls = []

        for part in parts:

            if "text" in part:
                text_parts.append(part["text"])

            elif "functionCall" in part:
                function = part["functionCall"]

                tool_calls.append(
                    ToolCall(
                        id=function.get("id", ""),
                        name=function["name"],
                        arguments=function.get(
                            "args",
                            {},
                        ),
                        thought_signature=part.get(
                            "thoughtSignature"
                        ),
                    )
                )

        return Response(
            text="\n".join(text_parts) or None,
            tool_calls=tool_calls or None,
        )

    def _response_message(
        self,
        response: Response,
    ) -> Message:

        return Message(
            role="assistant",
            content=response.text
        )

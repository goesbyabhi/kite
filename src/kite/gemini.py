import json
import os
from collections.abc import Iterator
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
                "GEMINI_API_KEY is not configured. Add it to your .env file."
            )

        self.api_key = api_key

    def complete(
        self,
        messages: list[Message],
        tools: list[dict],
        system: str | None = None,
    ) -> Response:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:generateContent"
        )

        payload = {
            "contents": self._build_contents(messages),
            **self._build_tools(tools),
        }

        if system:
            payload["systemInstruction"] = {
                "parts": [
                    {
                        "text": system,
                    }
                ]
            }

        response = httpx.post(
            url,
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )

        if response.is_error:
            raise RuntimeError(
                f"Gemini API Error ({response.status_code}): {response.text}"
            )

        data = response.json()

        # print(
        #     "[gemini]",
        #     {
        #         "parts": len(
        #             data["candidates"][0]["content"]["parts"]
        #         ),
        #         "finish_reason": data["candidates"][0].get(
        #             "finishReason"
        #         ),
        #     },
        # )

        return self._parse_response(data)

    def _build_contents(
        self,
        messages: list[Message],
    ) -> list[dict[str, Any]]:

        contents = []

        for message in messages:
            if message.role == "user":
                contents.append(
                    {
                        "role": "user",
                        "parts": [{"text": message.content}],
                    }
                )

            elif message.role == "assistant":
                parts = []

                if message.content:
                    parts.append({"text": message.content})

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

                contents.append(
                    {
                        "role": "model",
                        "parts": parts,
                    }
                )

            elif message.role == "tool":
                contents.append(
                    {
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
                    }
                )

        return contents

    def _build_tools(
        self,
        tools: list[dict],
    ) -> dict:

        if not tools:
            return {}

        return {"tools": [{"functionDeclarations": tools}]}

    def _parse_response(
        self,
        data: dict[str, Any],
    ) -> Response:
        candidates = data.get("candidates", [])

        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {data}")

        candidate = candidates[0]
        content = candidate.get("content")

        if not content:
            finish_reason = candidate.get(
                "finishReason",
                "UNKNOWN",
            )

            if finish_reason == "STOP":
                return Response()

            raise RuntimeError(
                f"Gemini returned no response content (finish reason: {finish_reason})."
            )

        parts = content.get("parts", [])

        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for part in parts:
            text = part.get("text")

            if text:
                text_parts.append(text)

            function = part.get("functionCall")

            if function:
                tool_calls.append(
                    ToolCall(
                        id=function.get("id", ""),
                        name=function["name"],
                        arguments=function.get("args", {}),
                        thought_signature=part.get("thoughtSignature"),
                    )
                )

        return Response(
            text="\n".join(text_parts) or None,
            tool_calls=tool_calls or None,
        )

    def stream(
        self,
        messages: list[Message],
        tools: list[dict],
        system: str | None = None,
    ) -> Iterator[str]:
        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:streamGenerateContent"
        )

        payload = {
            "contents": self._build_contents(messages),
            **self._build_tools(tools),
        }

        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        with httpx.stream(
            "POST",
            url,
            headers={
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json",
            },
            params={"alt": "sse"},
            json=payload,
            timeout=60,
        ) as response:
            if response.is_error:
                raise RuntimeError(
                    f"Gemini API Error ({response.status_code}): {response.text}"
                )

            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue

                data = json.loads(line[6:])

                for part in (
                    data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                ):
                    text = part.get("text")

                    if text:
                        yield text

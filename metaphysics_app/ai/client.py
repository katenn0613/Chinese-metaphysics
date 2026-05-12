"""LLM client adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


class LLMClient(Protocol):
    provider: str
    model: str

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return assistant text for the given conversation."""


class NullLLMClient:
    provider = "offline"
    model = "null"

    def complete(self, messages: list[ChatMessage]) -> str:
        user_message = next((message.content for message in reversed(messages) if message.role == "user"), "")
        return (
            "当前未配置 AI 服务。这是离线占位回复：\n"
            f"你的问题是：{user_message}\n"
            "排盘和基础解释仍可独立运行；配置 LLM adapter 后可生成深度分析。"
        )


class OpenAICompatibleClient:
    """Adapter for OpenAI-compatible chat completions.

    Import is lazy so the desktop shell and rule engine can run without AI deps.
    """

    provider = "openai-compatible"

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def complete(self, messages: list[ChatMessage]) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": message.role, "content": message.content} for message in messages],
        )
        return response.choices[0].message.content or ""

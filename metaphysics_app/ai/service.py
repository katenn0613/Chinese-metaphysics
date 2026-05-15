"""AI consultation use cases."""

from __future__ import annotations

from datetime import datetime

from metaphysics_app.ai.client import ChatMessage, LLMClient, build_default_llm_client
from metaphysics_app.ai.prompts import SYSTEM_PROMPT, build_bazi_context
from metaphysics_app.domain.models import (
    BaziChart,
    ConsultationMessage,
    FortuneConsultationSession,
    InterpretationResult,
)


class FortuneAIService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or build_default_llm_client()

    def ask_about_chart(
        self,
        question: str,
        chart: BaziChart | None = None,
        interpretation: InterpretationResult | None = None,
        session: FortuneConsultationSession | None = None,
    ) -> FortuneConsultationSession:
        session = session or FortuneConsultationSession(
            title=question[:30] or "AI 问命",
            chart_id=chart.id if chart else None,
            provider=self.llm_client.provider,
            model=self.llm_client.model,
        )

        messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
        if chart:
            messages.append(
                ChatMessage(role="user", content=build_bazi_context(chart, interpretation))
            )
        messages.extend(
            ChatMessage(role=message.role, content=message.content) for message in session.messages
        )
        messages.append(ChatMessage(role="user", content=question))

        answer = self.llm_client.complete(messages)
        session.messages.append(ConsultationMessage(role="user", content=question))
        session.messages.append(ConsultationMessage(role="assistant", content=answer))
        session.updated_at = datetime.now()
        return session


def consultation_session_from_payload(payload: dict) -> FortuneConsultationSession:
    kwargs = {
        "title": payload["title"],
        "chart_id": payload.get("chart_id"),
        "messages": [
            ConsultationMessage(
                role=message["role"],
                content=message["content"],
                created_at=_datetime_from_payload(message.get("created_at")),
            )
            for message in payload.get("messages", [])
        ],
        "provider": payload.get("provider", "offline"),
        "model": payload.get("model", "null"),
    }
    if payload.get("id"):
        kwargs["id"] = payload["id"]
    if payload.get("created_at"):
        kwargs["created_at"] = _datetime_from_payload(payload["created_at"])
    if payload.get("updated_at"):
        kwargs["updated_at"] = _datetime_from_payload(payload["updated_at"])
    return FortuneConsultationSession(**kwargs)


def _datetime_from_payload(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if value:
        return datetime.fromisoformat(value)
    return datetime.now()

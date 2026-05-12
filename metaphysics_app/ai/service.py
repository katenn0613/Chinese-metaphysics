"""AI consultation use cases."""

from __future__ import annotations

from metaphysics_app.ai.client import ChatMessage, LLMClient, NullLLMClient
from metaphysics_app.ai.prompts import SYSTEM_PROMPT, build_bazi_context
from metaphysics_app.domain.models import (
    BaziChart,
    ConsultationMessage,
    FortuneConsultationSession,
    InterpretationResult,
)


class FortuneAIService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or NullLLMClient()

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
            messages.append(ChatMessage(role="user", content=build_bazi_context(chart, interpretation)))
        messages.extend(ChatMessage(role=message.role, content=message.content) for message in session.messages)
        messages.append(ChatMessage(role="user", content=question))

        answer = self.llm_client.complete(messages)
        session.messages.append(ConsultationMessage(role="user", content=question))
        session.messages.append(ConsultationMessage(role="assistant", content=answer))
        return session

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from metaphysics_app.ai import FortuneAIService
from metaphysics_app.domain.models import BaziChart, FortuneConsultationSession, InterpretationResult
from metaphysics_app.ui.components import page_title, primary_button


class AIConsultationPage(QWidget):
    def __init__(self, ai_service: FortuneAIService) -> None:
        super().__init__()
        self.ai_service = ai_service
        self.chart: BaziChart | None = None
        self.interpretation: InterpretationResult | None = None
        self.session: FortuneConsultationSession | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("AI 问命"))

        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setMaximumHeight(120)
        self.context_text.setPlainText("尚未绑定排盘。可进行通用知识问答，但不会做个性化命盘分析。")
        layout.addWidget(self.context_text)

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        layout.addWidget(self.transcript, 1)

        input_row = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("输入你的问题，例如：这个盘的五行结构怎么理解？")
        send = primary_button("发送")
        send.clicked.connect(self.ask)
        self.question_input.returnPressed.connect(self.ask)
        input_row.addWidget(self.question_input, 1)
        input_row.addWidget(send)
        layout.addLayout(input_row)

    def set_context(self, chart: BaziChart, interpretation: InterpretationResult) -> None:
        self.chart = chart
        self.interpretation = interpretation
        self.session = None
        self.context_text.setPlainText(
            f"已绑定排盘：日主 {chart.day_master}，四柱 "
            + " / ".join(f"{pillar.name}:{pillar.label}" for pillar in chart.pillars)
        )

    def ask(self) -> None:
        question = self.question_input.text().strip()
        if not question:
            return
        self.session = self.ai_service.ask_about_chart(
            question=question,
            chart=self.chart,
            interpretation=self.interpretation,
            session=self.session,
        )
        self.question_input.clear()
        self._render_session()

    def _render_session(self) -> None:
        if not self.session:
            return
        self.transcript.setPlainText(
            "\n\n".join(f"{message.role}: {message.content}" for message in self.session.messages)
        )

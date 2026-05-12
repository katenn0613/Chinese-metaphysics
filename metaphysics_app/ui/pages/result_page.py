from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.services import BaziWorkflowResult
from metaphysics_app.ui.components import page_title, primary_button


class ResultPage(QWidget):
    save_requested = Signal()
    ai_requested = Signal()
    export_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.result: BaziWorkflowResult | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        layout.addWidget(page_title("排盘结果"))
        self.summary_label = QLabel("尚未生成排盘。")
        self.summary_label.setStyleSheet("font-size: 16px; color: #333;")
        layout.addWidget(self.summary_label)

        actions = QHBoxLayout()
        save = primary_button("保存记录")
        ai = QPushButton("AI 深度分析")
        export = QPushButton("导出报告")
        save.clicked.connect(self.save_requested.emit)
        ai.clicked.connect(self.ai_requested.emit)
        export.clicked.connect(self.export_requested.emit)
        actions.addWidget(save)
        actions.addWidget(ai)
        actions.addWidget(export)
        actions.addStretch()
        layout.addLayout(actions)

        tabs = QTabWidget()
        self.table = QTableWidget(4, 5)
        self.table.setHorizontalHeaderLabels(["柱", "天干", "地支", "藏干", "五行"])
        tabs.addTab(self.table, "基础排盘")

        self.beginner_text = QTextEdit()
        self.beginner_text.setReadOnly(True)
        tabs.addTab(self.beginner_text, "初学者模式")

        self.professional_text = QTextEdit()
        self.professional_text.setReadOnly(True)
        tabs.addTab(self.professional_text, "专业术语模式")

        self.chart_text = QTextEdit()
        self.chart_text.setReadOnly(True)
        tabs.addTab(self.chart_text, "图表数据")
        layout.addWidget(tabs, 1)

    def set_result(self, result: BaziWorkflowResult) -> None:
        self.result = result
        chart = result.chart
        self.summary_label.setText(
            f"日主 {chart.day_master} | 修正后时间 {chart.normalized_birth_datetime:%Y-%m-%d %H:%M}"
        )
        for row, pillar in enumerate(chart.pillars):
            values = [
                pillar.name,
                pillar.heavenly_stem,
                pillar.earthly_branch,
                " ".join(pillar.hidden_stems),
                pillar.five_element or "",
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

        self.beginner_text.setPlainText(self._interpretation_text(result.beginner_interpretation))
        self.professional_text.setPlainText(self._interpretation_text(result.professional_interpretation))
        self.chart_text.setPlainText(
            "五行分布：\n"
            + "\n".join(f"{key}: {value}" for key, value in chart.five_element_scores.items())
            + "\n\n阴阳分布：\n"
            + "\n".join(f"{key}: {value}" for key, value in chart.yin_yang_scores.items())
            + "\n\n计算备注：\n"
            + "\n".join(f"- {note}" for note in chart.calculation_notes)
        )

    def _interpretation_text(self, interpretation) -> str:
        sections = "\n\n".join(
            f"## {section.title}\n{section.content}" for section in interpretation.sections
        )
        notes = "\n".join(f"- {note}" for note in interpretation.confidence_notes)
        return f"{interpretation.summary}\n\n{sections}\n\n可信度备注：\n{notes}"

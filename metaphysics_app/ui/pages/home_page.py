from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from metaphysics_app.ui.components import BaguaWatermark, page_title


class HomePage(QWidget):
    open_bazi_requested = Signal()
    open_ai_requested = Signal()
    open_history_requested = Signal()
    open_almanac_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        layout.addWidget(page_title("工作台"))
        subtitle = QLabel("八字排盘、AI 问命、黄历择日与本地历史记录。")
        subtitle.setStyleSheet("color: #555;")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(14)
        self._add_entry(
            grid, 0, 0, "八字排盘", "输入出生信息，生成结构化盘面。", self.open_bazi_requested
        )
        self._add_entry(grid, 0, 1, "AI 问命", "基于盘面继续咨询式分析。", self.open_ai_requested)
        self._add_entry(
            grid, 1, 0, "历史记录", "查看、继续分析和导出本地命例。", self.open_history_requested
        )
        self._add_entry(
            grid, 1, 1, "黄历择日", "按用途和日期范围筛选候选日。", self.open_almanac_requested
        )
        layout.addLayout(grid)

        watermark = BaguaWatermark()
        layout.addWidget(watermark, 1)

    def _add_entry(self, grid, row: int, col: int, title: str, desc: str, signal: Signal) -> None:
        button = QPushButton(f"{title}\n{desc}")
        button.setMinimumHeight(88)
        button.setStyleSheet("text-align: left; font-size: 15px;")
        button.clicked.connect(signal.emit)
        grid.addWidget(button, row, col)

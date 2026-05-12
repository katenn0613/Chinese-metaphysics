from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from metaphysics_app.domain.models import HistoryRecord
from metaphysics_app.ui.components import page_title


class HistoryPage(QWidget):
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("历史记录"))

        actions = QHBoxLayout()
        refresh = QPushButton("刷新")
        refresh.clicked.connect(self.refresh_requested.emit)
        actions.addWidget(refresh)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["类型", "标题", "摘要", "标签", "更新时间"])
        layout.addWidget(self.table, 1)

    def set_records(self, records: list[HistoryRecord]) -> None:
        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            values = [
                record.record_type.value,
                record.title,
                record.preview_text,
                ", ".join(record.tags),
                record.updated_at.isoformat(timespec="minutes"),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

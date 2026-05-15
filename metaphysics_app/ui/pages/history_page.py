from __future__ import annotations

import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.domain.models import HistoryRecord
from metaphysics_app.ui.components import page_title


class HistoryPage(QWidget):
    refresh_requested = Signal()
    open_record_requested = Signal(object)
    export_record_requested = Signal(object)
    delete_record_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.all_records: list[HistoryRecord] = []
        self.records: list[HistoryRecord] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("历史记录"))

        actions = QHBoxLayout()
        self.type_filter = QComboBox()
        self.type_filter.addItem("全部类型", "")
        self.type_filter.addItem("八字", "bazi")
        self.type_filter.addItem("AI 对话", "ai_session")
        self.type_filter.addItem("黄历择日", "almanac")
        self.type_filter.addItem("导出", "export")
        self.type_filter.currentIndexChanged.connect(self._apply_filters)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索标题、摘要或标签")
        self.search_input.textChanged.connect(self._apply_filters)

        refresh = QPushButton("刷新")
        open_record = QPushButton("打开选中记录")
        export = QPushButton("导出选中记录")
        delete = QPushButton("删除选中记录")
        refresh.clicked.connect(self.refresh_requested.emit)
        open_record.clicked.connect(self._emit_open_selected)
        export.clicked.connect(self._emit_export_selected)
        delete.clicked.connect(self._emit_delete_selected)
        actions.addWidget(self.type_filter)
        actions.addWidget(self.search_input, 1)
        actions.addWidget(refresh)
        actions.addWidget(open_record)
        actions.addWidget(export)
        actions.addWidget(delete)
        actions.addStretch()
        layout.addLayout(actions)

        splitter = QSplitter()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["类型", "标题", "摘要", "标签", "更新时间"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self._render_selected_record)
        splitter.addWidget(self.table)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        splitter.addWidget(self.detail_text)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)

    def set_records(self, records: list[HistoryRecord]) -> None:
        self.all_records = records
        self._apply_filters()

    def _apply_filters(self) -> None:
        record_type = self.type_filter.currentData()
        keyword = self.search_input.text().strip().lower()
        records = self.all_records
        if record_type:
            records = [record for record in records if record.record_type.value == record_type]
        if keyword:
            records = [record for record in records if keyword in self._search_text(record).lower()]
        self._render_records(records)

    def _search_text(self, record: HistoryRecord) -> str:
        return " ".join([record.title, record.subtitle, record.preview_text, *record.tags])

    def _render_records(self, records: list[HistoryRecord]) -> None:
        self.records = records
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
        if records:
            self.table.selectRow(0)
        else:
            self.detail_text.setPlainText("暂无历史记录。")

    def _selected_record(self) -> HistoryRecord | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.records):
            return None
        return self.records[row]

    def _render_selected_record(self) -> None:
        record = self._selected_record()
        if record is None:
            self.detail_text.clear()
            return
        payload_json = json.dumps(record.payload, ensure_ascii=False, indent=2)
        self.detail_text.setPlainText(
            f"{record.title}\n\n"
            f"{record.subtitle}\n\n"
            f"{record.preview_text}\n\n"
            f"标签：{'、'.join(record.tags) if record.tags else '无'}\n"
            f"创建时间：{record.created_at.isoformat(timespec='minutes')}\n"
            f"更新时间：{record.updated_at.isoformat(timespec='minutes')}\n\n"
            f"{payload_json}"
        )

    def _emit_export_selected(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.export_record_requested.emit(record)

    def _emit_open_selected(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.open_record_requested.emit(record)

    def _emit_delete_selected(self) -> None:
        record = self._selected_record()
        if record is not None:
            self.delete_record_requested.emit(record)

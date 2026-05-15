from __future__ import annotations

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.engines.almanac import AlmanacSelector
from metaphysics_app.domain.models import AlmanacDateSelection
from metaphysics_app.ui.components import page_title, primary_button


class AlmanacPage(QWidget):
    save_selection_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.selector = AlmanacSelector()
        self.current_selection: AlmanacDateSelection | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("黄历择日"))

        form = QFormLayout()
        self.purpose_combo = QComboBox()
        for purpose in ["签约", "开工", "出行", "搬家", "会面"]:
            self.purpose_combo.addItem(purpose)
        form.addRow("用途", self.purpose_combo)

        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate().addDays(30))
        self.end_date.setCalendarPopup(True)
        form.addRow("开始日期", self.start_date)
        form.addRow("结束日期", self.end_date)

        self.weekend_checkbox = QCheckBox("优先周末")
        form.addRow("偏好", self.weekend_checkbox)
        layout.addLayout(form)

        actions = QHBoxLayout()
        select = primary_button("筛选日期")
        save = QPushButton("保存结果")
        select.clicked.connect(self.select_dates)
        save.clicked.connect(self._emit_save)
        actions.addWidget(select)
        actions.addWidget(save)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["日期", "等级", "评分", "原因"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

    def select_dates(self) -> None:
        start = self.start_date.date().toPython()
        end = self.end_date.date().toPython()
        if end < start:
            QMessageBox.warning(self, "日期范围有误", "结束日期不能早于开始日期。")
            return

        try:
            self.current_selection = self.selector.select_dates(
                purpose=self.purpose_combo.currentText(),
                start=start,
                end=end,
                constraints={"prefer_weekend": self.weekend_checkbox.isChecked()},
            )
        except ValueError as exc:
            QMessageBox.warning(self, "日期范围有误", str(exc))
            return
        self._render_selection()

    def set_selection(self, selection: AlmanacDateSelection) -> None:
        self.current_selection = selection
        purpose_index = self.purpose_combo.findText(selection.purpose)
        if purpose_index >= 0:
            self.purpose_combo.setCurrentIndex(purpose_index)
        self.start_date.setDate(
            QDate(
                selection.date_range_start.year,
                selection.date_range_start.month,
                selection.date_range_start.day,
            )
        )
        self.end_date.setDate(
            QDate(
                selection.date_range_end.year,
                selection.date_range_end.month,
                selection.date_range_end.day,
            )
        )
        self.weekend_checkbox.setChecked(bool(selection.constraints.get("prefer_weekend")))
        self._render_selection()

    def _render_selection(self) -> None:
        if self.current_selection is None:
            self.table.setRowCount(0)
            return
        self.table.setRowCount(len(self.current_selection.candidate_dates))
        for row, candidate in enumerate(self.current_selection.candidate_dates):
            values = [
                candidate.day.isoformat(),
                candidate.level,
                str(candidate.score),
                "；".join(candidate.reasons + candidate.warnings),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def _emit_save(self) -> None:
        if self.current_selection is None:
            QMessageBox.information(self, "暂无结果", "请先筛选日期。")
            return
        self.save_selection_requested.emit(self.current_selection)

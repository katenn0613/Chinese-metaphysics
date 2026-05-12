from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.engines.almanac import AlmanacSelector
from metaphysics_app.ui.components import page_title, primary_button


class AlmanacPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.selector = AlmanacSelector()
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
        select.clicked.connect(self.select_dates)
        actions.addWidget(select)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["日期", "等级", "评分", "原因"])
        layout.addWidget(self.table, 1)

    def select_dates(self) -> None:
        result = self.selector.select_dates(
            purpose=self.purpose_combo.currentText(),
            start=self.start_date.date().toPython(),
            end=self.end_date.date().toPython(),
            constraints={"prefer_weekend": self.weekend_checkbox.isChecked()},
        )
        self.table.setRowCount(len(result.candidate_dates))
        for row, candidate in enumerate(result.candidate_dates):
            values = [
                candidate.day.isoformat(),
                candidate.level,
                str(candidate.score),
                "；".join(candidate.reasons + candidate.warnings),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))

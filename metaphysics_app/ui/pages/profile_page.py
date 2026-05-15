from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.domain.models import Gender, UserProfile
from metaphysics_app.ui.components import page_title, primary_button


class ProfilePage(QWidget):
    refresh_requested = Signal()
    save_requested = Signal(object)
    delete_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.editing_profile_id: str | None = None
        self.profiles: list[UserProfile] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("用户信息"))

        form = QFormLayout()
        self.name_input = QLineEdit()
        form.addRow("姓名", self.name_input)

        self.gender_combo = QComboBox()
        self.gender_combo.addItem("未知", Gender.UNKNOWN.value)
        self.gender_combo.addItem("女", Gender.FEMALE.value)
        self.gender_combo.addItem("男", Gender.MALE.value)
        self.gender_combo.addItem("其他", Gender.OTHER.value)
        form.addRow("性别", self.gender_combo)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("用逗号分隔")
        form.addRow("标签", self.tags_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(88)
        form.addRow("备注", self.notes_input)
        layout.addLayout(form)

        actions = QHBoxLayout()
        save = primary_button("保存资料")
        load = QPushButton("载入选中资料")
        refresh = QPushButton("刷新")
        delete = QPushButton("删除选中资料")
        save.clicked.connect(self._emit_save)
        load.clicked.connect(self._load_selected)
        refresh.clicked.connect(self.refresh_requested.emit)
        delete.clicked.connect(self._emit_delete)
        actions.addWidget(save)
        actions.addWidget(load)
        actions.addWidget(refresh)
        actions.addWidget(delete)
        actions.addStretch()
        layout.addLayout(actions)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["姓名", "性别", "标签", "更新时间"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table, 1)

    def set_profiles(self, profiles: list[UserProfile]) -> None:
        self.profiles = profiles
        self.table.setRowCount(len(profiles))
        for row, profile in enumerate(profiles):
            values = [
                profile.display_name,
                profile.gender.value,
                "、".join(profile.tags),
                profile.updated_at.isoformat(timespec="minutes"),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        if profiles:
            self.table.selectRow(0)

    def clear_form(self) -> None:
        self.editing_profile_id = None
        self.name_input.clear()
        self.gender_combo.setCurrentIndex(0)
        self.tags_input.clear()
        self.notes_input.clear()

    def _emit_save(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "资料不完整", "姓名不能为空。")
            return
        self.save_requested.emit(
            {
                "id": self.editing_profile_id,
                "display_name": name,
                "gender": self.gender_combo.currentData(),
                "tags": [
                    tag.strip()
                    for tag in self.tags_input.text().replace("，", ",").split(",")
                    if tag.strip()
                ],
                "notes": self.notes_input.toPlainText().strip(),
            }
        )

    def _selected_profile(self) -> UserProfile | None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.profiles):
            return None
        return self.profiles[row]

    def _emit_delete(self) -> None:
        profile = self._selected_profile()
        if profile is not None:
            self.delete_requested.emit(profile)

    def _load_selected(self) -> None:
        profile = self._selected_profile()
        if profile is None:
            return
        self.editing_profile_id = profile.id
        self.name_input.setText(profile.display_name)
        gender_index = self.gender_combo.findData(profile.gender.value)
        if gender_index >= 0:
            self.gender_combo.setCurrentIndex(gender_index)
        self.tags_input.setText(", ".join(profile.tags))
        self.notes_input.setPlainText(profile.notes)

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.config import DEFAULT_TIMEZONE
from metaphysics_app.ui.components import page_title, primary_button


class SettingsPage(QWidget):
    save_requested = Signal(object)

    def __init__(
        self,
        database_path: str,
        export_dir: str,
        ai_provider: str,
        ai_model: str,
        initial_settings: dict[str, object] | None = None,
    ) -> None:
        super().__init__()
        initial_settings = initial_settings or {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("设置"))

        form = QFormLayout()
        self.timezone_input = QLineEdit(
            str(initial_settings.get("default_timezone", DEFAULT_TIMEZONE))
        )
        form.addRow("默认时区", self.timezone_input)

        self.true_solar_checkbox = QCheckBox("启用")
        self.true_solar_checkbox.setChecked(
            bool(initial_settings.get("default_true_solar_time", True))
        )
        form.addRow("默认真太阳时", self.true_solar_checkbox)

        form.addRow("数据库路径", QLabel(database_path))
        form.addRow("导出目录", QLabel(export_dir))
        form.addRow("AI 状态", QLabel(f"{ai_provider} / {ai_model}"))
        layout.addLayout(form)

        save = primary_button("保存设置")
        save.clicked.connect(self._save)
        layout.addWidget(save)
        layout.addStretch()

    def _save(self) -> None:
        timezone = self.timezone_input.text().strip() or DEFAULT_TIMEZONE
        try:
            ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            QMessageBox.warning(self, "设置有误", f"无法识别时区：{timezone}")
            return
        self.save_requested.emit(
            {
                "default_timezone": timezone,
                "default_true_solar_time": self.true_solar_checkbox.isChecked(),
            }
        )

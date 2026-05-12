from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from metaphysics_app.config import DEFAULT_DATABASE_PATH, DEFAULT_TIMEZONE
from metaphysics_app.ui.components import page_title


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(page_title("设置"))

        form = QFormLayout()
        theme = QComboBox()
        theme.addItems(["黑白克制", "浅色", "深色"])
        form.addRow("主题", theme)
        form.addRow("默认时区", QLineEdit(DEFAULT_TIMEZONE))
        form.addRow("默认真太阳时", QCheckBox("启用"))
        ai_mode = QComboBox()
        ai_mode.addItems(["离线占位", "OpenAI Compatible", "本地模型"])
        form.addRow("AI 模式", ai_mode)
        form.addRow("数据库路径", QLabel(str(DEFAULT_DATABASE_PATH)))
        layout.addLayout(form)
        layout.addStretch()

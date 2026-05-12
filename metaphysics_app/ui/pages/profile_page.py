from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from metaphysics_app.ui.components import page_title


class ProfilePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.addWidget(page_title("用户信息"))
        layout.addWidget(QLabel("V1 将在这里维护常用个人资料、出生信息、标签和研究备注。"))
        layout.addStretch()

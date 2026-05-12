"""Reusable UI components."""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QLabel, QPushButton, QWidget


def page_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 8px;")
    return label


def primary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("PrimaryButton")
    return button


class BaguaWatermark(QWidget):
    """Subtle black-white bagua-inspired mark for empty space."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(220, 220)

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 28
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(rect)
        painter.drawLine(rect.center().x(), rect.top(), rect.center().x(), rect.bottom())
        painter.drawArc(rect.adjusted(side * 0.25, 0, -side * 0.25, -side * 0.5), 90 * 16, 180 * 16)
        painter.drawArc(rect.adjusted(side * 0.25, side * 0.5, -side * 0.25, 0), -90 * 16, 180 * 16)

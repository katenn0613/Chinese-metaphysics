"""Black-and-white desktop theme."""

from __future__ import annotations


STYLE_SHEET = """
QWidget {
    background: #f7f7f5;
    color: #111111;
    font-size: 14px;
}
QMainWindow {
    background: #f7f7f5;
}
QFrame#Nav {
    background: #111111;
    border: none;
}
QLabel#AppTitle {
    color: #f6f2e8;
    font-size: 22px;
    font-weight: 700;
    padding: 18px 14px;
}
QPushButton {
    background: #ffffff;
    color: #111111;
    border: 1px solid #c9c9c3;
    border-radius: 6px;
    padding: 8px 12px;
}
QPushButton:hover {
    background: #eeeeea;
}
QPushButton#NavButton {
    background: transparent;
    color: #f6f2e8;
    border: none;
    border-radius: 4px;
    text-align: left;
    padding: 10px 16px;
}
QPushButton#NavButton:hover {
    background: #2a2a2a;
}
QPushButton#PrimaryButton {
    background: #111111;
    color: #ffffff;
    border: 1px solid #111111;
}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QDateTimeEdit, QDateEdit {
    background: #ffffff;
    border: 1px solid #c9c9c3;
    border-radius: 5px;
    padding: 6px;
}
QTableWidget {
    background: #ffffff;
    gridline-color: #d9d9d2;
    border: 1px solid #c9c9c3;
}
QHeaderView::section {
    background: #eeeeea;
    color: #111111;
    border: none;
    padding: 6px;
}
QTabWidget::pane {
    border: 1px solid #c9c9c3;
    background: #ffffff;
}
QTabBar::tab {
    background: #eeeeea;
    padding: 8px 14px;
}
QTabBar::tab:selected {
    background: #111111;
    color: #ffffff;
}
"""


def apply_theme(app: object) -> None:
    app.setStyleSheet(STYLE_SHEET)

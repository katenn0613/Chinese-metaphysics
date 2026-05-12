"""Desktop application bootstrap."""

from __future__ import annotations

import sys

from metaphysics_app.config import APP_NAME


def run() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ModuleNotFoundError:
        print("缺少 PySide6。请先运行：pip install -e '.[desktop]'")
        return 1

    from metaphysics_app.ui.main_window import MainWindow
    from metaphysics_app.ui.theme import apply_theme

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_theme(app)

    window = MainWindow()
    window.resize(1280, 820)
    window.show()
    return app.exec()

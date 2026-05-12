"""Main desktop window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.ai import FortuneAIService
from metaphysics_app.config import APP_NAME, DEFAULT_EXPORT_DIR
from metaphysics_app.data import Database, HistoryRepository
from metaphysics_app.domain.models import ExportFormat, HistoryRecord
from metaphysics_app.services import BaziWorkflowResult, BaziWorkflowService, ExportService
from metaphysics_app.ui.pages.ai_page import AIConsultationPage
from metaphysics_app.ui.pages.almanac_page import AlmanacPage
from metaphysics_app.ui.pages.bazi_input_page import BaziInputPage
from metaphysics_app.ui.pages.history_page import HistoryPage
from metaphysics_app.ui.pages.home_page import HomePage
from metaphysics_app.ui.pages.profile_page import ProfilePage
from metaphysics_app.ui.pages.result_page import ResultPage
from metaphysics_app.ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.database = Database()
        self.database.init_schema()
        self.history_repository = HistoryRepository(self.database)
        self.bazi_service = BaziWorkflowService(history_repository=self.history_repository)
        self.ai_service = FortuneAIService()
        self.export_service = ExportService()
        self.current_result: BaziWorkflowResult | None = None
        self.current_record: HistoryRecord | None = None

        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}
        self._build_pages()
        self._build_shell()
        self.show_page("home")

    def _build_shell(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        nav = QFrame()
        nav.setObjectName("Nav")
        nav.setFixedWidth(210)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("中国玄学")
        title.setObjectName("AppTitle")
        nav_layout.addWidget(title)

        nav_items = [
            ("home", "首页 / 工作台"),
            ("bazi", "八字排盘"),
            ("ai", "AI 问命"),
            ("almanac", "黄历择日"),
            ("history", "历史记录"),
            ("profile", "用户信息"),
            ("settings", "设置"),
        ]
        for key, label in nav_items:
            button = QPushButton(label)
            button.setObjectName("NavButton")
            button.clicked.connect(lambda checked=False, page_key=key: self.show_page(page_key))
            nav_layout.addWidget(button)
        nav_layout.addStretch()

        layout.addWidget(nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

    def _build_pages(self) -> None:
        home = HomePage()
        home.open_bazi_requested.connect(lambda: self.show_page("bazi"))
        home.open_ai_requested.connect(lambda: self.show_page("ai"))
        home.open_history_requested.connect(lambda: self.show_page("history"))
        home.open_almanac_requested.connect(lambda: self.show_page("almanac"))

        bazi = BaziInputPage()
        bazi.generate_requested.connect(self.generate_bazi)

        result = ResultPage()
        result.save_requested.connect(self.save_current_result)
        result.ai_requested.connect(self.open_ai_for_current_result)
        result.export_requested.connect(self.export_current_record)

        ai = AIConsultationPage(self.ai_service)

        history = HistoryPage()
        history.refresh_requested.connect(self.refresh_history)

        self.pages = {
            "home": home,
            "bazi": bazi,
            "result": result,
            "ai": ai,
            "almanac": AlmanacPage(),
            "history": history,
            "profile": ProfilePage(),
            "settings": SettingsPage(),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

    def show_page(self, key: str) -> None:
        if key == "history":
            self.refresh_history()
        self.stack.setCurrentWidget(self.pages[key])

    def generate_bazi(self, birth_info) -> None:
        try:
            self.current_result = self.bazi_service.generate_chart(birth_info)
            self.current_record = None
            result_page = self.pages["result"]
            assert isinstance(result_page, ResultPage)
            result_page.set_result(self.current_result)
            self.show_page("result")
        except Exception as exc:  # pragma: no cover - UI guard
            QMessageBox.critical(self, "排盘失败", str(exc))

    def save_current_result(self) -> None:
        if not self.current_result:
            QMessageBox.information(self, "暂无结果", "请先生成排盘。")
            return
        self.current_record = self.bazi_service.save_result(self.current_result)
        QMessageBox.information(self, "已保存", "记录已保存到本地历史。")

    def open_ai_for_current_result(self) -> None:
        ai_page = self.pages["ai"]
        assert isinstance(ai_page, AIConsultationPage)
        if self.current_result:
            ai_page.set_context(
                self.current_result.chart,
                self.current_result.beginner_interpretation,
            )
        self.show_page("ai")

    def export_current_record(self) -> None:
        if self.current_record is None:
            if self.current_result is None:
                QMessageBox.information(self, "暂无记录", "请先生成并保存记录。")
                return
            self.current_record = self.bazi_service.save_result(self.current_result)

        output_path = Path(DEFAULT_EXPORT_DIR) / f"{self.current_record.title}.md"
        try:
            self.export_service.export_history_record(
                self.current_record,
                output_path,
                ExportFormat.MARKDOWN,
            )
            QMessageBox.information(self, "导出完成", f"已导出：{output_path}")
        except Exception as exc:  # pragma: no cover - UI guard
            QMessageBox.critical(self, "导出失败", str(exc))

    def refresh_history(self) -> None:
        history_page = self.pages["history"]
        assert isinstance(history_page, HistoryPage)
        history_page.set_records(self.history_repository.list_recent())

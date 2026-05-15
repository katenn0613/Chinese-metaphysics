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

from metaphysics_app.ai import FortuneAIService, consultation_session_from_payload
from metaphysics_app.config import APP_NAME, DEFAULT_EXPORT_DIR, DEFAULT_TIMEZONE
from metaphysics_app.data import (
    Database,
    HistoryRepository,
    SettingsRepository,
    UserProfileRepository,
)
from metaphysics_app.domain.models import (
    AlmanacDateSelection,
    ExportFormat,
    FortuneConsultationSession,
    Gender,
    HistoryRecord,
    HistoryRecordType,
    UserProfile,
)
from metaphysics_app.engines.almanac import almanac_selection_from_payload
from metaphysics_app.services import (
    BaziWorkflowResult,
    BaziWorkflowService,
    ExportService,
    safe_report_filename,
)
from metaphysics_app.ui.pages.ai_page import AIConsultationPage
from metaphysics_app.ui.pages.almanac_page import AlmanacPage
from metaphysics_app.ui.pages.bazi_input_page import BaziInputPage
from metaphysics_app.ui.pages.history_page import HistoryPage
from metaphysics_app.ui.pages.home_page import HomePage
from metaphysics_app.ui.pages.profile_page import ProfilePage
from metaphysics_app.ui.pages.result_page import ResultPage
from metaphysics_app.ui.pages.settings_page import SettingsPage
from metaphysics_app.utils.serialization import to_jsonable


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.database = Database()
        self.database.init_schema()
        self.history_repository = HistoryRepository(self.database)
        self.settings_repository = SettingsRepository(self.database)
        self.profile_repository = UserProfileRepository(self.database)
        self.app_settings = self._load_app_settings()
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

        bazi = BaziInputPage(
            default_timezone=str(self.app_settings["default_timezone"]),
            default_true_solar_time=bool(self.app_settings["default_true_solar_time"]),
        )
        bazi.generate_requested.connect(self.generate_bazi)

        result = ResultPage()
        result.save_requested.connect(self.save_current_result)
        result.ai_requested.connect(self.open_ai_for_current_result)
        result.export_requested.connect(self.export_current_record)

        ai = AIConsultationPage(self.ai_service)
        ai.save_session_requested.connect(self.save_ai_session)

        history = HistoryPage()
        history.refresh_requested.connect(self.refresh_history)
        history.open_record_requested.connect(self.open_history_record)
        history.export_record_requested.connect(self.export_history_record)
        history.delete_record_requested.connect(self.delete_history_record)

        settings = SettingsPage(
            database_path=str(self.database.path),
            export_dir=str(DEFAULT_EXPORT_DIR),
            ai_provider=self.ai_service.llm_client.provider,
            ai_model=self.ai_service.llm_client.model,
            initial_settings=self.app_settings,
        )
        settings.save_requested.connect(self.save_settings)

        profile = ProfilePage()
        profile.refresh_requested.connect(self.refresh_profiles)
        profile.save_requested.connect(self.save_profile)
        profile.delete_requested.connect(self.delete_profile)

        self.pages = {
            "home": home,
            "bazi": bazi,
            "result": result,
            "ai": ai,
            "almanac": self._build_almanac_page(),
            "history": history,
            "profile": profile,
            "settings": settings,
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

    def _build_almanac_page(self) -> AlmanacPage:
        page = AlmanacPage()
        page.save_selection_requested.connect(self.save_almanac_selection)
        return page

    def _load_app_settings(self) -> dict[str, object]:
        return self.settings_repository.get_many(
            {
                "default_timezone": DEFAULT_TIMEZONE,
                "default_true_solar_time": True,
            }
        )

    def show_page(self, key: str) -> None:
        if key == "history":
            self.refresh_history()
        if key == "profile":
            self.refresh_profiles()
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

        self.export_history_record(self.current_record)

    def export_history_record(self, record: HistoryRecord) -> None:
        output_path = Path(DEFAULT_EXPORT_DIR) / safe_report_filename(
            f"{record.title}-{record.id[:8]}"
        )
        try:
            self.export_service.export_history_record(
                record,
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

    def save_settings(self, settings: dict[str, object]) -> None:
        self.settings_repository.set_many(settings)
        self.app_settings = self._load_app_settings()
        bazi_page = self.pages["bazi"]
        assert isinstance(bazi_page, BaziInputPage)
        bazi_page.apply_defaults(
            default_timezone=str(self.app_settings["default_timezone"]),
            default_true_solar_time=bool(self.app_settings["default_true_solar_time"]),
        )
        QMessageBox.information(self, "已保存", "设置已保存。")

    def delete_history_record(self, record: HistoryRecord) -> None:
        answer = QMessageBox.question(self, "确认删除", f"删除记录：{record.title}？")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.history_repository.delete(record.id)
        if self.current_record and self.current_record.id == record.id:
            self.current_record = None
        self.refresh_history()

    def save_ai_session(self, session: FortuneConsultationSession) -> None:
        assistant_messages = [
            message.content for message in session.messages if message.role == "assistant"
        ]
        record = HistoryRecord(
            record_type=HistoryRecordType.AI_SESSION,
            title=session.title or "AI 问命对话",
            subtitle=f"{session.provider} / {session.model}",
            preview_text=assistant_messages[-1][:120] if assistant_messages else "",
            payload=to_jsonable(session),
            tags=["AI", "问命"],
        )
        self.history_repository.save(record)
        QMessageBox.information(self, "已保存", "AI 对话已保存到历史记录。")

    def open_history_record(self, record: HistoryRecord) -> None:
        try:
            if record.record_type == HistoryRecordType.BAZI:
                self.current_result = self.bazi_service.load_result(record)
                self.current_record = record
                result_page = self.pages["result"]
                assert isinstance(result_page, ResultPage)
                result_page.set_result(self.current_result)
                self.show_page("result")
                return
            if record.record_type == HistoryRecordType.AI_SESSION:
                ai_page = self.pages["ai"]
                assert isinstance(ai_page, AIConsultationPage)
                ai_page.set_session(consultation_session_from_payload(record.payload))
                self.show_page("ai")
                return
            if record.record_type == HistoryRecordType.ALMANAC:
                almanac_page = self.pages["almanac"]
                assert isinstance(almanac_page, AlmanacPage)
                almanac_page.set_selection(almanac_selection_from_payload(record.payload))
                self.show_page("almanac")
                return
            QMessageBox.information(self, "暂不支持打开", "该记录可在历史详情中查看。")
        except Exception as exc:  # pragma: no cover - UI guard
            QMessageBox.critical(self, "打开失败", str(exc))

    def refresh_profiles(self) -> None:
        profile_page = self.pages["profile"]
        assert isinstance(profile_page, ProfilePage)
        profile_page.set_profiles(self.profile_repository.list_recent())

    def save_profile(self, data: dict[str, object]) -> None:
        profile_id = data.get("id")
        profile = UserProfile(
            display_name=str(data["display_name"]),
            gender=Gender(data["gender"]),
            notes=str(data.get("notes", "")),
            tags=list(data.get("tags", [])),
        )
        if profile_id:
            profile.id = str(profile_id)
        self.profile_repository.save(profile)
        profile_page = self.pages["profile"]
        assert isinstance(profile_page, ProfilePage)
        profile_page.clear_form()
        self.refresh_profiles()
        QMessageBox.information(self, "已保存", "用户资料已保存。")

    def delete_profile(self, profile: UserProfile) -> None:
        answer = QMessageBox.question(self, "确认删除", f"删除资料：{profile.display_name}？")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.profile_repository.delete(profile.id)
        self.refresh_profiles()

    def save_almanac_selection(self, selection: AlmanacDateSelection) -> None:
        preview = "；".join(
            f"{candidate.day.isoformat()} {candidate.level}{candidate.score}"
            for candidate in selection.candidate_dates[:3]
        )
        record = HistoryRecord(
            record_type=HistoryRecordType.ALMANAC,
            title=f"黄历择日 {selection.purpose}",
            subtitle=f"{selection.date_range_start} 至 {selection.date_range_end}",
            preview_text=preview or "未筛选到候选日期",
            payload=to_jsonable(selection),
            tags=["黄历", "择日", selection.purpose],
        )
        self.history_repository.save(record)
        QMessageBox.information(self, "已保存", "择日结果已保存到历史记录。")

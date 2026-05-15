from datetime import datetime

from metaphysics_app.data import (
    Database,
    HistoryRepository,
    SettingsRepository,
    UserProfileRepository,
)
from metaphysics_app.domain.models import (
    BirthInfo,
    ExportFormat,
    Gender,
    HistoryRecord,
    HistoryRecordType,
    UserProfile,
)
from metaphysics_app.ai import FortuneAIService
from metaphysics_app.engines.almanac import AlmanacSelector
from metaphysics_app.services import BaziWorkflowService, ExportService, safe_report_filename
from metaphysics_app.utils.serialization import to_jsonable


def test_history_repository_round_trips_records(tmp_path):
    database = Database(tmp_path / "app.sqlite3")
    database.init_schema()
    repository = HistoryRepository(database)
    record = HistoryRecord(
        record_type=HistoryRecordType.BAZI,
        title="八字排盘",
        subtitle="日主 甲",
        preview_text="摘要",
        payload={"created": datetime(2024, 2, 10, 9, 30), "pillars": ["甲辰"]},
        tags=["八字"],
    )

    repository.save(record)
    records = repository.list_recent()

    assert len(records) == 1
    assert records[0].title == "八字排盘"
    assert records[0].payload["created"] == "2024-02-10T09:30:00"
    assert records[0].created_at.microsecond == record.created_at.microsecond
    assert repository.delete(record.id) is True
    assert repository.list_recent() == []


def test_history_repository_orders_by_precise_updated_time(tmp_path):
    database = Database(tmp_path / "app.sqlite3")
    database.init_schema()
    repository = HistoryRepository(database)
    older = HistoryRecord(
        record_type=HistoryRecordType.BAZI,
        title="较早",
        payload={},
        updated_at=datetime(2024, 1, 1, 1, 1, 1, 1),
    )
    newer = HistoryRecord(
        record_type=HistoryRecordType.BAZI,
        title="较晚",
        payload={},
        updated_at=datetime(2024, 1, 1, 1, 1, 1, 2),
    )

    repository.save(older)
    repository.save(newer)

    assert [record.title for record in repository.list_recent()] == ["较晚", "较早"]


def test_settings_repository_persists_json_values(tmp_path):
    database = Database(tmp_path / "app.sqlite3")
    database.init_schema()
    repository = SettingsRepository(database)

    repository.set_many({"default_timezone": "Asia/Tokyo", "default_true_solar_time": False})

    assert repository.get("default_timezone") == "Asia/Tokyo"
    assert repository.get_many({"default_timezone": "UTC", "missing": 3}) == {
        "default_timezone": "Asia/Tokyo",
        "missing": 3,
    }
    assert repository.get_many({}) == {}


def test_bazi_history_record_can_restore_workflow_result():
    service = BaziWorkflowService()
    result = service.generate_chart(
        BirthInfo(datetime(2024, 2, 10, 9, 30), use_true_solar_time=False)
    )
    record = service.save_result(result, title="可恢复排盘")

    restored = service.load_result(record)

    assert [pillar.label for pillar in restored.chart.pillars] == ["甲辰", "丙寅", "甲辰", "己巳"]
    assert restored.beginner_interpretation.summary == result.beginner_interpretation.summary


def test_user_profile_repository_round_trips_profiles(tmp_path):
    database = Database(tmp_path / "app.sqlite3")
    database.init_schema()
    repository = UserProfileRepository(database)
    profile = UserProfile(
        display_name="测试用户",
        gender=Gender.FEMALE,
        notes="长期案例",
        tags=["研究", "八字"],
    )

    repository.save(profile)
    profiles = repository.list_recent()

    assert profiles[0].display_name == "测试用户"
    assert profiles[0].gender == Gender.FEMALE
    assert profiles[0].tags == ["研究", "八字"]
    profile.display_name = "更新用户"
    repository.save(profile)
    assert repository.list_recent()[0].display_name == "更新用户"
    assert repository.delete(profile.id) is True
    assert repository.list_recent() == []


def test_user_profile_repository_round_trips_birth_info(tmp_path):
    database = Database(tmp_path / "app.sqlite3")
    database.init_schema()
    repository = UserProfileRepository(database)
    profile = UserProfile(
        display_name="带生日用户",
        birth_info=BirthInfo(datetime(2024, 2, 10, 9, 30), longitude=121.47, latitude=31.23),
        tags=["生日"],
    )

    repository.save(profile)
    restored = repository.list_recent()[0]

    assert restored.birth_info is not None
    assert restored.birth_info.birth_datetime == datetime(2024, 2, 10, 9, 30)
    assert restored.birth_info.longitude == 121.47


def test_user_profile_normalizes_name_and_gender_string():
    profile = UserProfile(display_name=" 测试 ", gender="male")

    assert profile.display_name == "测试"
    assert profile.gender == Gender.MALE


def test_history_record_accepts_type_string_and_normalizes_title():
    record = HistoryRecord(record_type="bazi", title=" 标题 ", payload={})

    assert record.record_type == HistoryRecordType.BAZI
    assert record.title == "标题"


def test_markdown_export_writes_pretty_json_and_safe_filename(tmp_path):
    record = HistoryRecord(
        record_type=HistoryRecordType.BAZI,
        title="八字: 2024/02/10",
        subtitle="日主 甲",
        preview_text="摘要",
        payload={"pillars": ["甲辰", "丙寅"]},
        tags=["八字", "排盘"],
    )
    output_path = tmp_path / safe_report_filename(record.title)

    task = ExportService().export_history_record(record, output_path, export_format="markdown")

    assert task.status == "finished"
    assert output_path.name == "八字_ 2024_02_10.md"
    content = output_path.read_text(encoding="utf-8")
    assert "## 结构化数据" in content
    assert '"pillars": [' in content


def test_safe_report_filename_limits_length():
    filename = safe_report_filename("甲" * 200, max_length=20)

    assert len(filename) == 20
    assert filename.endswith(".md")


def test_bazi_markdown_export_includes_readable_report(tmp_path):
    service = BaziWorkflowService()
    result = service.generate_chart(
        BirthInfo(datetime(2024, 2, 10, 9, 30), use_true_solar_time=False)
    )
    record = service.save_result(result, title="八字报告")
    output_path = tmp_path / "report.md"

    ExportService().export_history_record(record, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "| 年柱 | 甲 | 辰 |" in content
    assert "## 初学者解读" in content
    assert "## 专业解读" in content


def test_almanac_markdown_export_includes_candidate_table(tmp_path):
    selection = AlmanacSelector().select_dates(
        "签约",
        datetime(2026, 5, 18).date(),
        datetime(2026, 5, 25).date(),
    )
    record = HistoryRecord(
        record_type=HistoryRecordType.ALMANAC,
        title="黄历择日 签约",
        subtitle="2026-05-18 至 2026-05-25",
        preview_text="候选日期",
        payload=to_jsonable(selection),
        tags=["黄历", "择日"],
    )
    output_path = tmp_path / "almanac.md"

    ExportService().export_history_record(record, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "## 候选日期" in content
    assert "| 日期 | 等级 | 评分 | 原因 | 注意事项 |" in content


def test_ai_session_markdown_export_includes_transcript(tmp_path):
    session = FortuneAIService().ask_about_chart("请解释这个问题")
    record = HistoryRecord(
        record_type=HistoryRecordType.AI_SESSION,
        title="AI 问命",
        subtitle="offline / null",
        preview_text="对话",
        payload=to_jsonable(session),
        tags=["AI"],
    )
    output_path = tmp_path / "ai.md"

    ExportService().export_history_record(record, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "## 对话记录" in content
    assert "### 用户" in content
    assert "请解释这个问题" in content


def test_export_service_rejects_unimplemented_formats(tmp_path):
    record = HistoryRecord(
        record_type=HistoryRecordType.BAZI,
        title="报告",
        payload={},
    )

    try:
        ExportService().export_history_record(
            record,
            tmp_path / "report.pdf",
            export_format=ExportFormat.PDF,
        )
    except NotImplementedError:
        pass
    else:
        raise AssertionError("unimplemented export format should fail")

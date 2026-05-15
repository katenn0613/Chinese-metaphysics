from datetime import datetime

from metaphysics_app.domain.models import BirthInfo, CalendarType, Gender
from metaphysics_app.services import BaziWorkflowService


def test_bazi_workflow_returns_chart_and_interpretations():
    service = BaziWorkflowService()
    result = service.generate_chart(
        BirthInfo(
            birth_datetime=datetime(1998, 6, 13, 9, 30),
            calendar_type=CalendarType.SOLAR,
            birthplace_name="Shanghai",
            timezone="Asia/Shanghai",
            gender=Gender.UNKNOWN,
            use_true_solar_time=True,
            longitude=121.47,
            latitude=31.23,
        )
    )

    assert len(result.chart.pillars) == 4
    assert result.chart.day_master
    assert result.beginner_interpretation.summary
    assert result.professional_interpretation.summary


def test_bazi_core_uses_known_sexagenary_day_and_solar_month():
    service = BaziWorkflowService()
    result = service.generate_chart(
        BirthInfo(
            birth_datetime=datetime(2024, 2, 10, 9, 30),
            calendar_type=CalendarType.SOLAR,
            timezone="Asia/Shanghai",
            use_true_solar_time=False,
        )
    )

    assert [pillar.label for pillar in result.chart.pillars] == ["甲辰", "丙寅", "甲辰", "己巳"]
    assert [pillar.ten_god for pillar in result.chart.pillars] == ["比肩", "食神", "日主", "正财"]
    assert result.chart.algorithm_version == "bazi-core-v0.2"


def test_bazi_year_switches_at_approximate_li_chun():
    service = BaziWorkflowService()
    before = service.generate_chart(
        BirthInfo(datetime(1984, 2, 3, 12, 0), use_true_solar_time=False)
    )
    after = service.generate_chart(
        BirthInfo(datetime(1984, 2, 4, 12, 0), use_true_solar_time=False)
    )

    assert before.chart.pillars[0].label == "癸亥"
    assert after.chart.pillars[0].label == "甲子"


def test_bazi_solar_month_handles_early_january_boundary():
    service = BaziWorkflowService()
    before_minor_cold = service.generate_chart(
        BirthInfo(datetime(2025, 1, 1, 12, 0), use_true_solar_time=False)
    )
    after_minor_cold = service.generate_chart(
        BirthInfo(datetime(2025, 1, 6, 12, 0), use_true_solar_time=False)
    )

    assert before_minor_cold.chart.pillars[1].earthly_branch == "子"
    assert after_minor_cold.chart.pillars[1].earthly_branch == "丑"


def test_birth_info_rejects_invalid_longitude():
    try:
        BirthInfo(datetime(2024, 1, 1), longitude=300)
    except ValueError as exc:
        assert "经度" in str(exc)
    else:
        raise AssertionError("invalid longitude should fail")


def test_birth_info_normalizes_timezone_whitespace():
    birth_info = BirthInfo(datetime(2024, 1, 1), timezone=" Asia/Shanghai ")

    assert birth_info.timezone == "Asia/Shanghai"


def test_birth_info_accepts_enum_values_as_strings():
    birth_info = BirthInfo(
        datetime(2024, 1, 1),
        calendar_type="solar",
        gender="female",
    )

    assert birth_info.calendar_type == CalendarType.SOLAR
    assert birth_info.gender == Gender.FEMALE

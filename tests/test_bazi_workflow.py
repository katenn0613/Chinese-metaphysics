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

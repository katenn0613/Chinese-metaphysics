"""Application service for the Bazi workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from metaphysics_app.data.repositories import HistoryRepository
from metaphysics_app.domain.models import (
    BaziChart,
    BirthInfo,
    CalendarType,
    Gender,
    HistoryRecord,
    HistoryRecordType,
    InterpretationMode,
    InterpretationResult,
    InterpretationSection,
    Pillar,
)
from metaphysics_app.engines.bazi import BaziCalculator
from metaphysics_app.interpretation import BaziInterpreter
from metaphysics_app.utils.serialization import to_jsonable


@dataclass(slots=True)
class BaziWorkflowResult:
    chart: BaziChart
    beginner_interpretation: InterpretationResult
    professional_interpretation: InterpretationResult


class BaziWorkflowService:
    def __init__(
        self,
        calculator: BaziCalculator | None = None,
        interpreter: BaziInterpreter | None = None,
        history_repository: HistoryRepository | None = None,
    ) -> None:
        self.calculator = calculator or BaziCalculator()
        self.interpreter = interpreter or BaziInterpreter()
        self.history_repository = history_repository

    def generate_chart(self, birth_info: BirthInfo) -> BaziWorkflowResult:
        chart = self.calculator.calculate(birth_info)
        beginner = self.interpreter.interpret(chart, InterpretationMode.BEGINNER)
        professional = self.interpreter.interpret(chart, InterpretationMode.PROFESSIONAL)
        return BaziWorkflowResult(
            chart=chart,
            beginner_interpretation=beginner,
            professional_interpretation=professional,
        )

    def save_result(self, result: BaziWorkflowResult, title: str | None = None) -> HistoryRecord:
        record = HistoryRecord(
            record_type=HistoryRecordType.BAZI,
            title=title or f"八字排盘 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            subtitle=f"日主 {result.chart.day_master}",
            preview_text=result.beginner_interpretation.summary,
            payload=to_jsonable(result),
            tags=["八字", "排盘"],
        )
        if self.history_repository:
            self.history_repository.save(record)
        return record

    def load_result(self, record: HistoryRecord) -> BaziWorkflowResult:
        if record.record_type != HistoryRecordType.BAZI:
            raise ValueError("只能从八字历史记录恢复排盘结果。")
        return bazi_workflow_result_from_payload(record.payload)


def bazi_workflow_result_from_payload(payload: dict) -> BaziWorkflowResult:
    return BaziWorkflowResult(
        chart=_chart_from_payload(payload["chart"]),
        beginner_interpretation=_interpretation_from_payload(payload["beginner_interpretation"]),
        professional_interpretation=_interpretation_from_payload(
            payload["professional_interpretation"]
        ),
    )


def _chart_from_payload(payload: dict) -> BaziChart:
    kwargs = {
        "birth_info": _birth_info_from_payload(payload["birth_info"]),
        "normalized_birth_datetime": _datetime_from_payload(payload["normalized_birth_datetime"]),
        "pillars": [_pillar_from_payload(item) for item in payload["pillars"]],
        "day_master": payload["day_master"],
        "five_element_scores": payload["five_element_scores"],
        "yin_yang_scores": payload["yin_yang_scores"],
        "algorithm_version": payload["algorithm_version"],
        "calculation_notes": payload.get("calculation_notes", []),
    }
    if payload.get("id"):
        kwargs["id"] = payload["id"]
    if payload.get("created_at"):
        kwargs["created_at"] = _datetime_from_payload(payload["created_at"])
    return BaziChart(**kwargs)


def _birth_info_from_payload(payload: dict) -> BirthInfo:
    return BirthInfo(
        birth_datetime=_datetime_from_payload(payload["birth_datetime"]),
        calendar_type=CalendarType(payload.get("calendar_type", CalendarType.SOLAR.value)),
        birthplace_name=payload.get("birthplace_name", ""),
        timezone=payload.get("timezone", "Asia/Shanghai"),
        gender=Gender(payload.get("gender", Gender.UNKNOWN.value)),
        use_true_solar_time=payload.get("use_true_solar_time", True),
        longitude=payload.get("longitude"),
        latitude=payload.get("latitude"),
    )


def _pillar_from_payload(payload: dict) -> Pillar:
    return Pillar(
        name=payload["name"],
        heavenly_stem=payload["heavenly_stem"],
        earthly_branch=payload["earthly_branch"],
        hidden_stems=payload.get("hidden_stems", []),
        ten_god=payload.get("ten_god"),
        five_element=payload.get("five_element"),
    )


def _interpretation_from_payload(payload: dict) -> InterpretationResult:
    kwargs = {
        "chart_id": payload["chart_id"],
        "mode": InterpretationMode(payload["mode"]),
        "summary": payload["summary"],
        "sections": [
            InterpretationSection(
                title=item["title"],
                content=item["content"],
                tags=item.get("tags", []),
            )
            for item in payload.get("sections", [])
        ],
        "generator_version": payload.get("generator_version", "rules-template-v0.1"),
        "follow_up_questions": payload.get("follow_up_questions", []),
        "confidence_notes": payload.get("confidence_notes", []),
    }
    if payload.get("id"):
        kwargs["id"] = payload["id"]
    if payload.get("created_at"):
        kwargs["created_at"] = _datetime_from_payload(payload["created_at"])
    return InterpretationResult(**kwargs)


def _datetime_from_payload(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

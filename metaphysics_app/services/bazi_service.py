"""Application service for the Bazi workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from metaphysics_app.data.repositories import HistoryRepository
from metaphysics_app.domain.models import (
    BaziChart,
    BirthInfo,
    HistoryRecord,
    HistoryRecordType,
    InterpretationMode,
    InterpretationResult,
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

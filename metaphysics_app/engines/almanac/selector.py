"""V1 almanac date-selection heuristic engine."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from metaphysics_app.domain.models import AlmanacCandidateDate, AlmanacDateSelection


PURPOSE_WEEKDAY_BONUSES = {
    "签约": {1, 2, 3},
    "开工": {1, 2, 3},
    "出行": {4, 5, 6},
    "搬家": {5, 6},
    "会面": {1, 2, 3, 4},
}


class AlmanacSelector:
    algorithm_version = "almanac-heuristic-v0.2"
    max_range_days = 366

    def select_dates(
        self,
        purpose: str,
        start: date,
        end: date,
        constraints: dict[str, Any] | None = None,
    ) -> AlmanacDateSelection:
        if end < start:
            raise ValueError("结束日期不能早于开始日期。")
        if (end - start).days + 1 > self.max_range_days:
            raise ValueError(f"择日范围不能超过 {self.max_range_days} 天。")

        constraints = constraints or {}
        candidates: list[AlmanacCandidateDate] = []
        current = start
        while current <= end:
            score, reasons = self._score_day(current, purpose, constraints)
            if score >= 60:
                candidates.append(
                    AlmanacCandidateDate(
                        day=current,
                        score=score,
                        level="推荐" if score >= 75 else "可用",
                        reasons=reasons,
                        warnings=["当前为启发式择日评分，正式黄历宜忌和冲煞规则仍待接入。"],
                    )
                )
            current += timedelta(days=1)
        candidates.sort(key=lambda candidate: (-candidate.score, candidate.day))

        return AlmanacDateSelection(
            purpose=purpose,
            date_range_start=start,
            date_range_end=end,
            constraints=constraints,
            candidate_dates=candidates,
        )

    def _score_day(
        self, day: date, purpose: str, constraints: dict[str, Any]
    ) -> tuple[int, list[str]]:
        score = 50 + (day.toordinal() % 12) * 2
        reasons = [f"基础周期分 {score}"]
        if constraints.get("prefer_weekend") and day.weekday() >= 5:
            score += 10
            reasons.append("符合周末偏好 +10")
        if day.weekday() in PURPOSE_WEEKDAY_BONUSES.get(purpose, set()):
            score += 8
            reasons.append(f"符合{purpose}常用星期偏好 +8")
        return min(score, 95), reasons


def almanac_selection_from_payload(payload: dict) -> AlmanacDateSelection:
    kwargs = {
        "purpose": payload["purpose"],
        "date_range_start": _date_from_payload(payload["date_range_start"]),
        "date_range_end": _date_from_payload(payload["date_range_end"]),
        "constraints": payload.get("constraints", {}),
        "candidate_dates": [
            AlmanacCandidateDate(
                day=_date_from_payload(candidate["day"]),
                score=candidate["score"],
                level=candidate["level"],
                reasons=candidate.get("reasons", []),
                warnings=candidate.get("warnings", []),
            )
            for candidate in payload.get("candidate_dates", [])
        ],
    }
    if payload.get("id"):
        kwargs["id"] = payload["id"]
    if payload.get("created_at"):
        kwargs["created_at"] = _datetime_from_payload(payload["created_at"])
    return AlmanacDateSelection(**kwargs)


def _date_from_payload(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _datetime_from_payload(value):
    if isinstance(value, datetime):
        return value
    if value:
        return datetime.fromisoformat(value)
    return datetime.now()

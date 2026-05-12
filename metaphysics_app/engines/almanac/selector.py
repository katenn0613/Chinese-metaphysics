"""V1 almanac date-selection skeleton."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from metaphysics_app.domain.models import AlmanacCandidateDate, AlmanacDateSelection


class AlmanacSelector:
    algorithm_version = "almanac-skeleton-v0.1"

    def select_dates(
        self,
        purpose: str,
        start: date,
        end: date,
        constraints: dict[str, Any] | None = None,
    ) -> AlmanacDateSelection:
        constraints = constraints or {}
        candidates: list[AlmanacCandidateDate] = []
        current = start
        while current <= end:
            score = self._placeholder_score(current, purpose, constraints)
            if score >= 60:
                candidates.append(
                    AlmanacCandidateDate(
                        day=current,
                        score=score,
                        level="推荐" if score >= 75 else "可用",
                        reasons=[f"{purpose}用途占位评分 {score}"],
                        warnings=["当前为择日规则骨架，需接入正式黄历规则。"],
                    )
                )
            current += timedelta(days=1)

        return AlmanacDateSelection(
            purpose=purpose,
            date_range_start=start,
            date_range_end=end,
            constraints=constraints,
            candidate_dates=candidates,
        )

    def _placeholder_score(self, day: date, purpose: str, constraints: dict[str, Any]) -> int:
        base = 50 + (day.toordinal() % 40)
        if constraints.get("prefer_weekend") and day.weekday() >= 5:
            base += 8
        if purpose in {"签约", "开工", "会面"} and day.weekday() in {1, 2, 3}:
            base += 5
        return min(base, 95)

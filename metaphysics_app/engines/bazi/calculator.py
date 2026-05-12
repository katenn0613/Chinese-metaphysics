"""Initial Bazi calculator skeleton.

The class returns a complete structured object, but several calendar-sensitive
details are marked as placeholders until a validated almanac/solar-term module
is introduced.
"""

from __future__ import annotations

from datetime import datetime

from metaphysics_app.domain.models import BaziChart, BirthInfo, Pillar
from metaphysics_app.engines.bazi.calendar import CalendarNormalizer
from metaphysics_app.engines.bazi.constants import (
    BRANCH_ELEMENTS,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    HIDDEN_STEMS,
    STEM_ELEMENTS,
    STEM_YIN_YANG,
)


class BaziCalculator:
    algorithm_version = "bazi-skeleton-v0.1"

    def __init__(self, calendar_normalizer: CalendarNormalizer | None = None) -> None:
        self.calendar_normalizer = calendar_normalizer or CalendarNormalizer()

    def calculate(self, birth_info: BirthInfo) -> BaziChart:
        normalized = self.calendar_normalizer.normalize(birth_info)
        calculation_time = normalized.calculation_datetime

        year_pillar = self._sexagenary_year_pillar(calculation_time.year)
        month_pillar = self._placeholder_month_pillar(calculation_time)
        day_pillar = self._placeholder_day_pillar(calculation_time)
        hour_pillar = self._placeholder_hour_pillar(calculation_time, day_pillar.heavenly_stem)
        pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]

        return BaziChart(
            birth_info=birth_info,
            normalized_birth_datetime=calculation_time,
            pillars=pillars,
            day_master=day_pillar.heavenly_stem,
            five_element_scores=self._five_element_scores(pillars),
            yin_yang_scores=self._yin_yang_scores(pillars),
            algorithm_version=self.algorithm_version,
            calculation_notes=[
                *normalized.notes,
                "年柱使用 1984 甲子年基准做骨架计算。",
                "月柱、日柱、时柱当前为可替换占位算法，后续需接入节气与万年历校验。",
            ],
        )

    def _sexagenary_year_pillar(self, year: int) -> Pillar:
        index = (year - 1984) % 60
        return self._make_pillar("年柱", index % 10, index % 12)

    def _placeholder_month_pillar(self, value: datetime) -> Pillar:
        index = (value.year * 12 + value.month) % 60
        return self._make_pillar("月柱", index % 10, index % 12)

    def _placeholder_day_pillar(self, value: datetime) -> Pillar:
        index = value.toordinal() % 60
        return self._make_pillar("日柱", index % 10, index % 12)

    def _placeholder_hour_pillar(self, value: datetime, day_stem: str) -> Pillar:
        branch_index = ((value.hour + 1) // 2) % 12
        day_stem_index = HEAVENLY_STEMS.index(day_stem)
        stem_index = (day_stem_index * 2 + branch_index) % 10
        return self._make_pillar("时柱", stem_index, branch_index)

    def _make_pillar(self, name: str, stem_index: int, branch_index: int) -> Pillar:
        stem = HEAVENLY_STEMS[stem_index]
        branch = EARTHLY_BRANCHES[branch_index]
        return Pillar(
            name=name,
            heavenly_stem=stem,
            earthly_branch=branch,
            hidden_stems=HIDDEN_STEMS.get(branch, []),
            five_element=STEM_ELEMENTS[stem],
        )

    def _five_element_scores(self, pillars: list[Pillar]) -> dict[str, int]:
        scores = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        for pillar in pillars:
            scores[STEM_ELEMENTS[pillar.heavenly_stem]] += 1
            scores[BRANCH_ELEMENTS[pillar.earthly_branch]] += 1
        return scores

    def _yin_yang_scores(self, pillars: list[Pillar]) -> dict[str, int]:
        scores = {"阳": 0, "阴": 0}
        for pillar in pillars:
            scores[STEM_YIN_YANG[pillar.heavenly_stem]] += 1
        return scores

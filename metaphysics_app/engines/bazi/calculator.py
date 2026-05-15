"""Bazi calculator with deterministic stem/branch rules."""

from __future__ import annotations

from datetime import date, datetime

from metaphysics_app.domain.models import BaziChart, BirthInfo, Pillar
from metaphysics_app.engines.bazi.calendar import CalendarNormalizer
from metaphysics_app.engines.bazi.constants import (
    APPROXIMATE_SOLAR_MONTH_STARTS,
    BRANCH_ELEMENTS,
    EARTHLY_BRANCHES,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    HEAVENLY_STEMS,
    HIDDEN_STEMS,
    MONTH_BRANCHES_BY_SOLAR_TERM,
    STEM_ELEMENTS,
    STEM_YIN_YANG,
)


class BaziCalculator:
    algorithm_version = "bazi-core-v0.2"

    def __init__(self, calendar_normalizer: CalendarNormalizer | None = None) -> None:
        self.calendar_normalizer = calendar_normalizer or CalendarNormalizer()

    def calculate(self, birth_info: BirthInfo) -> BaziChart:
        normalized = self.calendar_normalizer.normalize(birth_info)
        calculation_time = normalized.calculation_datetime

        sexagenary_year = self._sexagenary_year(calculation_time)
        year_pillar = self._sexagenary_year_pillar(sexagenary_year)
        month_pillar = self._solar_month_pillar(calculation_time, year_pillar.heavenly_stem)
        day_pillar = self._sexagenary_day_pillar(calculation_time.date())
        hour_pillar = self._hour_pillar(calculation_time, day_pillar.heavenly_stem)
        pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
        self._assign_ten_gods(pillars, day_pillar.heavenly_stem)

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
                f"年柱按近似立春切年，干支年记为 {sexagenary_year}。",
                "月柱按固定公历节气边界近似定月，后续可替换为精确天文节气。",
                "日柱按儒略日数推算六十甲子，时柱按日干起时规则生成。",
            ],
        )

    def _sexagenary_year(self, value: datetime) -> int:
        if (value.month, value.day) < (2, 4):
            return value.year - 1
        return value.year

    def _sexagenary_year_pillar(self, year: int) -> Pillar:
        index = (year - 1984) % 60
        return self._make_pillar("年柱", index % 10, index % 12)

    def _solar_month_pillar(self, value: datetime, year_stem: str) -> Pillar:
        month_index, branch = self._solar_month_index_and_branch(value.date())
        year_stem_index = HEAVENLY_STEMS.index(year_stem)
        first_month_stem_index = ((year_stem_index % 5) * 2 + 2) % 10
        stem_index = (first_month_stem_index + month_index) % 10
        return self._make_pillar("月柱", stem_index, EARTHLY_BRANCHES.index(branch))

    def _solar_month_index_and_branch(self, value: date) -> tuple[int, str]:
        boundaries: list[tuple[date, str]] = []
        for month, day, _term_name in APPROXIMATE_SOLAR_MONTH_STARTS:
            boundary_year = value.year if month != 1 else value.year + 1
            boundaries.append(
                (date(boundary_year, month, day), MONTH_BRANCHES_BY_SOLAR_TERM[len(boundaries)])
            )

        if value < boundaries[0][0]:
            return (10, "子") if value < date(value.year, 1, 6) else (11, "丑")

        for index, (boundary, branch) in enumerate(boundaries):
            next_boundary = boundaries[index + 1][0] if index + 1 < len(boundaries) else None
            if next_boundary is None or boundary <= value < next_boundary:
                return index, branch

        return 11, "丑"

    def _sexagenary_day_pillar(self, value: date) -> Pillar:
        index = (self._julian_day_number(value) + 49) % 60
        return self._make_pillar("日柱", index % 10, index % 12)

    def _julian_day_number(self, value: date) -> int:
        month = value.month
        year = value.year
        day = value.day
        adjust = (14 - month) // 12
        year = year + 4800 - adjust
        month = month + 12 * adjust - 3
        return (
            day
            + (153 * month + 2) // 5
            + 365 * year
            + year // 4
            - year // 100
            + year // 400
            - 32045
        )

    def _hour_pillar(self, value: datetime, day_stem: str) -> Pillar:
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

    def _assign_ten_gods(self, pillars: list[Pillar], day_master: str) -> None:
        for pillar in pillars:
            if pillar.name == "日柱":
                pillar.ten_god = "日主"
            else:
                pillar.ten_god = self._ten_god(day_master, pillar.heavenly_stem)

    def _ten_god(self, day_master: str, other_stem: str) -> str:
        day_element = STEM_ELEMENTS[day_master]
        other_element = STEM_ELEMENTS[other_stem]
        same_polarity = STEM_YIN_YANG[day_master] == STEM_YIN_YANG[other_stem]

        if other_element == day_element:
            return "比肩" if same_polarity else "劫财"
        if ELEMENT_GENERATES[day_element] == other_element:
            return "食神" if same_polarity else "伤官"
        if ELEMENT_CONTROLS[day_element] == other_element:
            return "偏财" if same_polarity else "正财"
        if ELEMENT_GENERATES[other_element] == day_element:
            return "偏印" if same_polarity else "正印"
        if ELEMENT_CONTROLS[other_element] == day_element:
            return "七杀" if same_polarity else "正官"
        return "未定"

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

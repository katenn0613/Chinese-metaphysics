"""Calendar normalization for Bazi calculations.

The public interface is intentionally separate from the Bazi calculator so lunar
conversion and true solar time can be replaced with a validated calendar module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from metaphysics_app.domain.models import BirthInfo, CalendarType
from metaphysics_app.engines.bazi.constants import TIMEZONE_STANDARD_MERIDIANS


@dataclass(slots=True)
class NormalizedBirthTime:
    original: datetime
    solar_datetime: datetime
    calculation_datetime: datetime
    notes: list[str] = field(default_factory=list)


class CalendarNormalizer:
    """Normalize calendar input before rule calculation.

    V1 keeps a conservative placeholder for lunar conversion. The interface is
    ready for a precise Chinese calendar/solar-term implementation.
    """

    def normalize(self, birth_info: BirthInfo) -> NormalizedBirthTime:
        notes: list[str] = []
        solar_datetime = birth_info.birth_datetime

        if birth_info.calendar_type == CalendarType.LUNAR:
            notes.append("农历转阳历接口已预留，当前骨架暂按输入时间继续计算。")

        calculation_datetime = solar_datetime
        if birth_info.use_true_solar_time:
            calculation_datetime = self._apply_true_solar_time(solar_datetime, birth_info, notes)

        return NormalizedBirthTime(
            original=birth_info.birth_datetime,
            solar_datetime=solar_datetime,
            calculation_datetime=calculation_datetime,
            notes=notes,
        )

    def _apply_true_solar_time(
        self,
        solar_datetime: datetime,
        birth_info: BirthInfo,
        notes: list[str],
    ) -> datetime:
        if birth_info.longitude is None:
            notes.append("未提供经度，真太阳时修正已跳过。")
            return solar_datetime

        standard_meridian = TIMEZONE_STANDARD_MERIDIANS.get(birth_info.timezone, 120.0)
        minute_offset = round((birth_info.longitude - standard_meridian) * 4)
        notes.append(
            f"真太阳时按经度差做基础修正：标准经线 {standard_meridian}°，"
            f"出生地经度 {birth_info.longitude}°，修正 {minute_offset} 分钟。"
        )
        notes.append("均时差修正接口已预留，当前骨架未纳入精确天文修正。")
        return solar_datetime + timedelta(minutes=minute_offset)

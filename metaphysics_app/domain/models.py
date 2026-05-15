"""Domain models shared by engines, services, persistence, and UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class CalendarType(str, Enum):
    SOLAR = "solar"
    LUNAR = "lunar"


class Gender(str, Enum):
    FEMALE = "female"
    MALE = "male"
    OTHER = "other"
    UNKNOWN = "unknown"


class InterpretationMode(str, Enum):
    PROFESSIONAL = "professional"
    BEGINNER = "beginner"


class HistoryRecordType(str, Enum):
    BAZI = "bazi"
    AI_SESSION = "ai_session"
    ALMANAC = "almanac"
    EXPORT = "export"


class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    PNG = "png"


@dataclass(slots=True)
class BirthInfo:
    birth_datetime: datetime
    calendar_type: CalendarType = CalendarType.SOLAR
    birthplace_name: str = ""
    timezone: str = "Asia/Shanghai"
    gender: Gender = Gender.UNKNOWN
    use_true_solar_time: bool = True
    longitude: float | None = None
    latitude: float | None = None

    def __post_init__(self) -> None:
        if isinstance(self.calendar_type, str):
            self.calendar_type = CalendarType(self.calendar_type)
        if isinstance(self.gender, str):
            self.gender = Gender(self.gender)
        if not isinstance(self.birth_datetime, datetime):
            raise ValueError("出生时间必须是 datetime 类型。")
        if not isinstance(self.timezone, str):
            raise ValueError("时区必须是字符串。")
        self.timezone = self.timezone.strip()
        if not self.timezone:
            raise ValueError("时区不能为空。")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"无法识别时区：{self.timezone}") from exc
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValueError("经度必须在 -180 到 180 之间。")
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValueError("纬度必须在 -90 到 90 之间。")


@dataclass(slots=True)
class UserProfile:
    display_name: str
    birth_info: BirthInfo | None = None
    gender: Gender = Gender.UNKNOWN
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.display_name = self.display_name.strip()
        if not self.display_name:
            raise ValueError("用户资料姓名不能为空。")
        if isinstance(self.gender, str):
            self.gender = Gender(self.gender)


@dataclass(slots=True)
class Pillar:
    name: str
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str] = field(default_factory=list)
    ten_god: str | None = None
    five_element: str | None = None

    @property
    def label(self) -> str:
        return f"{self.heavenly_stem}{self.earthly_branch}"


@dataclass(slots=True)
class BaziChart:
    birth_info: BirthInfo
    normalized_birth_datetime: datetime
    pillars: list[Pillar]
    day_master: str
    five_element_scores: dict[str, int]
    yin_yang_scores: dict[str, int]
    algorithm_version: str
    calculation_notes: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class InterpretationSection:
    title: str
    content: str
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class InterpretationResult:
    chart_id: str
    mode: InterpretationMode
    summary: str
    sections: list[InterpretationSection]
    generator_version: str = "rules-template-v0.1"
    follow_up_questions: list[str] = field(default_factory=list)
    confidence_notes: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class ConsultationMessage:
    role: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class FortuneConsultationSession:
    title: str
    chart_id: str | None = None
    messages: list[ConsultationMessage] = field(default_factory=list)
    provider: str = "offline"
    model: str = "null"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class AlmanacCandidateDate:
    day: date
    score: int
    level: str
    reasons: list[str]
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AlmanacDateSelection:
    purpose: str
    date_range_start: date
    date_range_end: date
    constraints: dict[str, Any]
    candidate_dates: list[AlmanacCandidateDate]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)


@dataclass(slots=True)
class HistoryRecord:
    record_type: HistoryRecordType
    title: str
    payload: dict[str, Any]
    subtitle: str = ""
    preview_text: str = ""
    tags: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if isinstance(self.record_type, str):
            self.record_type = HistoryRecordType(self.record_type)
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("历史记录标题不能为空。")


@dataclass(slots=True)
class ReportTemplate:
    id: str
    name: str
    description: str
    supported_formats: list[ExportFormat]


@dataclass(slots=True)
class ExportTask:
    record_id: str
    template_id: str
    export_format: ExportFormat
    output_path: str
    status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None

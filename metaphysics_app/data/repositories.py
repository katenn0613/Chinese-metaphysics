"""Repository layer for local SQLite persistence."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from metaphysics_app.data.database import Database
from metaphysics_app.domain.models import (
    BirthInfo,
    CalendarType,
    Gender,
    HistoryRecord,
    HistoryRecordType,
    UserProfile,
)
from metaphysics_app.utils.serialization import to_jsonable


class HistoryRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, record: HistoryRecord) -> None:
        payload_json = json.dumps(to_jsonable(record.payload), ensure_ascii=False)
        tags_json = json.dumps(record.tags, ensure_ascii=False)
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO history_records (
                    id, record_type, title, subtitle, preview_text,
                    tags_json, payload_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.record_type.value,
                    record.title,
                    record.subtitle,
                    record.preview_text,
                    tags_json,
                    payload_json,
                    record.created_at.isoformat(timespec="microseconds"),
                    record.updated_at.isoformat(timespec="microseconds"),
                ),
            )

    def list_recent(self, limit: int = 20) -> list[HistoryRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM history_records
                ORDER BY updated_at DESC, created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._row_to_record(row) for row in rows]

    def delete(self, record_id: str) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM history_records WHERE id = ?", (record_id,))
        return cursor.rowcount > 0

    def _row_to_record(self, row: Any) -> HistoryRecord:
        return HistoryRecord(
            id=row["id"],
            record_type=HistoryRecordType(row["record_type"]),
            title=row["title"],
            subtitle=row["subtitle"],
            preview_text=row["preview_text"],
            tags=json.loads(row["tags_json"]),
            payload=json.loads(row["payload_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class SettingsRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self, key: str, default: Any = None) -> Any:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT value_json FROM app_settings WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return default
        return json.loads(row["value_json"])

    def get_many(self, defaults: dict[str, Any]) -> dict[str, Any]:
        if not defaults:
            return {}
        values = defaults.copy()
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT key, value_json FROM app_settings WHERE key IN ({})".format(
                    ",".join("?" for _ in defaults)
                ),
                tuple(defaults.keys()),
            ).fetchall()
        for row in rows:
            values[row["key"]] = json.loads(row["value_json"])
        return values

    def set(self, key: str, value: Any) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        value_json = json.dumps(to_jsonable(value), ensure_ascii=False)
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_settings (key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (key, value_json, now),
            )

    def set_many(self, values: dict[str, Any]) -> None:
        if not values:
            return
        now = datetime.now().isoformat(timespec="seconds")
        rows = [
            (key, json.dumps(to_jsonable(value), ensure_ascii=False), now)
            for key, value in values.items()
        ]
        with self.database.connect() as connection:
            connection.executemany(
                """
                INSERT INTO app_settings (key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                rows,
            )


class UserProfileRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, profile: UserProfile) -> None:
        profile.updated_at = datetime.now()
        birth_info_json = (
            json.dumps(to_jsonable(profile.birth_info), ensure_ascii=False)
            if profile.birth_info
            else None
        )
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO user_profiles (
                    id, display_name, birth_info_json, gender, notes,
                    tags_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    display_name = excluded.display_name,
                    birth_info_json = excluded.birth_info_json,
                    gender = excluded.gender,
                    notes = excluded.notes,
                    tags_json = excluded.tags_json,
                    updated_at = excluded.updated_at
                """,
                (
                    profile.id,
                    profile.display_name,
                    birth_info_json,
                    profile.gender.value,
                    profile.notes,
                    json.dumps(profile.tags, ensure_ascii=False),
                    profile.created_at.isoformat(timespec="microseconds"),
                    profile.updated_at.isoformat(timespec="microseconds"),
                ),
            )

    def list_recent(self, limit: int = 50) -> list[UserProfile]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM user_profiles
                ORDER BY updated_at DESC, created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def delete(self, profile_id: str) -> bool:
        with self.database.connect() as connection:
            cursor = connection.execute("DELETE FROM user_profiles WHERE id = ?", (profile_id,))
        return cursor.rowcount > 0

    def _row_to_profile(self, row: Any) -> UserProfile:
        birth_info_payload = json.loads(row["birth_info_json"]) if row["birth_info_json"] else None
        return UserProfile(
            id=row["id"],
            display_name=row["display_name"],
            birth_info=_birth_info_from_payload(birth_info_payload) if birth_info_payload else None,
            gender=Gender(row["gender"]),
            notes=row["notes"],
            tags=json.loads(row["tags_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


def _birth_info_from_payload(payload: dict[str, Any]) -> BirthInfo:
    return BirthInfo(
        birth_datetime=datetime.fromisoformat(payload["birth_datetime"]),
        calendar_type=CalendarType(payload.get("calendar_type", CalendarType.SOLAR.value)),
        birthplace_name=payload.get("birthplace_name", ""),
        timezone=payload.get("timezone", "Asia/Shanghai"),
        gender=Gender(payload.get("gender", Gender.UNKNOWN.value)),
        use_true_solar_time=payload.get("use_true_solar_time", True),
        longitude=payload.get("longitude"),
        latitude=payload.get("latitude"),
    )

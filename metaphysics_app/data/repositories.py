"""Repository layer for local SQLite persistence."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from metaphysics_app.data.database import Database
from metaphysics_app.domain.models import HistoryRecord, HistoryRecordType
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
                    record.created_at.isoformat(timespec="seconds"),
                    record.updated_at.isoformat(timespec="seconds"),
                ),
            )

    def list_recent(self, limit: int = 20) -> list[HistoryRecord]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM history_records
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._row_to_record(row) for row in rows]

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

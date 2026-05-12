"""SQLite connection management."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from metaphysics_app.config import DEFAULT_DATABASE_PATH
from metaphysics_app.data.schema import SCHEMA_SQL


class Database:
    def __init__(self, path: Path | str = DEFAULT_DATABASE_PATH) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_schema(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA_SQL)

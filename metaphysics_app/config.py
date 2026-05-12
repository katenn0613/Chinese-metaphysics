"""Runtime configuration defaults."""

from __future__ import annotations

from pathlib import Path


APP_NAME = "中国玄学"
APP_SLUG = "chinese_metaphysics"
DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_DATA_DIR = Path.home() / ".chinese_metaphysics"
DEFAULT_DATABASE_PATH = DEFAULT_DATA_DIR / "metaphysics.sqlite3"
DEFAULT_EXPORT_DIR = DEFAULT_DATA_DIR / "exports"


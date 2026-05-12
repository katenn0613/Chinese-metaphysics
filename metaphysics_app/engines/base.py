"""Engine protocols used by application services."""

from __future__ import annotations

from typing import Protocol

from metaphysics_app.domain.models import BaziChart, BirthInfo


class BaziCalculatorProtocol(Protocol):
    def calculate(self, birth_info: BirthInfo) -> BaziChart:
        """Return a structured Bazi chart from normalized birth information."""

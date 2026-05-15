"""Application entrypoint."""

from __future__ import annotations

import argparse
from datetime import datetime

from metaphysics_app import __version__
from metaphysics_app.domain.models import BirthInfo
from metaphysics_app.services import BaziWorkflowService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chinese metaphysics desktop app")
    parser.add_argument("--version", action="store_true", help="print package version and exit")
    parser.add_argument(
        "--smoke", action="store_true", help="run a headless rule-engine smoke check"
    )
    args, _unknown = parser.parse_known_args(argv)

    if args.version:
        print(__version__)
        return 0
    if args.smoke:
        return _run_smoke_check()

    from metaphysics_app.ui.app import run

    return run()


def _run_smoke_check() -> int:
    result = BaziWorkflowService().generate_chart(
        BirthInfo(datetime(2024, 2, 10, 9, 30), use_true_solar_time=False)
    )
    pillars = " / ".join(
        f"{pillar.name}:{pillar.label}({pillar.ten_god})" for pillar in result.chart.pillars
    )
    print(f"version={__version__}")
    print(f"algorithm={result.chart.algorithm_version}")
    print(f"pillars={pillars}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Application entrypoint."""

from __future__ import annotations


def main() -> int:
    from metaphysics_app.ui.app import run

    return run()


if __name__ == "__main__":
    raise SystemExit(main())

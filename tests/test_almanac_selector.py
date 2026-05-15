from datetime import date, datetime

from metaphysics_app.engines.almanac import AlmanacSelector, almanac_selection_from_payload
from metaphysics_app.utils.serialization import to_jsonable


def test_almanac_selector_orders_candidates_by_score():
    selector = AlmanacSelector()

    result = selector.select_dates(
        purpose="签约",
        start=date(2026, 5, 18),
        end=date(2026, 5, 25),
        constraints={"prefer_weekend": False},
    )

    scores = [candidate.score for candidate in result.candidate_dates]
    assert scores == sorted(scores, reverse=True)
    assert result.candidate_dates[0].reasons
    assert selector.algorithm_version == "almanac-heuristic-v0.2"


def test_almanac_selector_rejects_invalid_ranges():
    selector = AlmanacSelector()

    try:
        selector.select_dates("签约", date(2026, 5, 20), date(2026, 5, 1))
    except ValueError as exc:
        assert "结束日期" in str(exc)
    else:
        raise AssertionError("invalid date range should fail")

    try:
        selector.select_dates("签约", date(2026, 1, 1), date(2027, 1, 2))
    except ValueError as exc:
        assert "366" in str(exc)
    else:
        raise AssertionError("overlong date range should fail")


def test_almanac_selection_round_trips_from_payload():
    selector = AlmanacSelector()
    result = selector.select_dates("签约", date(2026, 5, 18), date(2026, 5, 25))

    restored = almanac_selection_from_payload(to_jsonable(result))

    assert restored.purpose == "签约"
    assert restored.candidate_dates[0].day == result.candidate_dates[0].day


def test_almanac_selection_payload_accepts_datetime_values():
    payload = {
        "purpose": "签约",
        "date_range_start": datetime(2026, 5, 18, 9, 0),
        "date_range_end": datetime(2026, 5, 20, 9, 0),
        "constraints": {},
        "candidate_dates": [],
    }

    restored = almanac_selection_from_payload(payload)

    assert restored.date_range_start == date(2026, 5, 18)

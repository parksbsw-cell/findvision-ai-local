from datetime import datetime, timedelta, timezone

from app.analytics import Analytics


def test_retention_uses_korean_dates_and_distinct_return_days(tmp_path):
    analytics = Analytics(tmp_path / "analytics.db")
    korea = timezone(timedelta(hours=9))
    today = datetime.now(korea).date()
    rows = [
        ("a", "visit", datetime.combine(today - timedelta(days=8), datetime.min.time(), korea).isoformat()),
        ("a", "visit", datetime.combine(today - timedelta(days=7), datetime.min.time(), korea).isoformat()),
        ("a", "visit", datetime.combine(today - timedelta(days=2), datetime.min.time(), korea).isoformat()),
        ("a", "generated", datetime.now(korea).isoformat()),
        ("b", "visit", datetime.combine(today - timedelta(days=8), datetime.min.time(), korea).isoformat()),
    ]
    with analytics._connect() as db:
        db.executemany("INSERT INTO events(visitor, kind, created_at) VALUES (?, ?, ?)", rows)

    summary = analytics.summary()
    assert summary["visitors"] == 2
    assert summary["returning_visitors"] == 1
    assert summary["returning_days"] == 2
    assert summary["retention_percent"] == 50.0
    assert summary["d1_retention_percent"] == 50.0
    assert summary["d7_retention_percent"] == 50.0
    assert summary["generation_conversion_percent"] == 50.0


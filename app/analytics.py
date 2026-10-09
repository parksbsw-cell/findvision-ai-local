import sqlite3
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path


class Analytics:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "CREATE TABLE IF NOT EXISTS events (visitor TEXT NOT NULL, kind TEXT NOT NULL, "
                "created_at TEXT NOT NULL)"
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def record(self, visitor: str, kind: str) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO events(visitor, kind, created_at) VALUES (?, ?, ?)",
                (visitor, kind, datetime.now(UTC).isoformat()),
            )

    def summary(self) -> dict[str, float | int]:
        with self._connect() as db:
            visit_rows = db.execute(
                "SELECT visitor, created_at FROM events WHERE kind='visit' ORDER BY created_at"
            ).fetchall()
            generated = db.execute(
                "SELECT COUNT(*) FROM events WHERE kind='generated'"
            ).fetchone()[0]
            generators = db.execute(
                "SELECT COUNT(DISTINCT visitor) FROM events WHERE kind='generated'"
            ).fetchone()[0]

        korea = timezone(timedelta(hours=9))
        today = datetime.now(korea).date()
        days_by_visitor: dict[str, set[date]] = defaultdict(set)
        for visitor, created_at in visit_rows:
            timestamp = datetime.fromisoformat(created_at)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            days_by_visitor[visitor].add(timestamp.astimezone(korea).date())

        visit_counts: dict[str, int] = defaultdict(int)
        for visitor, _ in visit_rows:
            visit_counts[visitor] += 1
        visitors = len(days_by_visitor)
        # Product metric: count each browser once as a new visit. Its second
        # session and later sessions belong to returning usage instead.
        visits = visitors
        returning = sum(count > 1 for count in visit_counts.values())
        returning_days = sum(max(0, count - 1) for count in visit_counts.values())
        recent = sum(any(day >= today - timedelta(days=6) for day in days) for days in days_by_visitor.values())

        d1_eligible = d1_returned = d7_eligible = d7_returned = 0
        for days in days_by_visitor.values():
            first = min(days)
            if first <= today - timedelta(days=1):
                d1_eligible += 1
                d1_returned += first + timedelta(days=1) in days
            if first <= today - timedelta(days=7):
                d7_eligible += 1
                d7_returned += any(first < day <= first + timedelta(days=7) for day in days)
        return {
            "visits": visits,
            "visitors": visitors,
            "returning_visitors": returning,
            "retention_percent": round(returning / visitors * 100, 1) if visitors else 0.0,
            "returning_days": returning_days,
            "d1_retention_percent": round(d1_returned / d1_eligible * 100, 1) if d1_eligible else 0.0,
            "d7_retention_percent": round(d7_returned / d7_eligible * 100, 1) if d7_eligible else 0.0,
            "generated": generated,
            "generation_conversion_percent": round(generators / visitors * 100, 1) if visitors else 0.0,
            "visitors_7d": recent,
        }


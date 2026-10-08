import sqlite3
from datetime import UTC, datetime, timedelta
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
            visits = db.execute("SELECT COUNT(*) FROM events WHERE kind='visit'").fetchone()[0]
            visitors = db.execute(
                "SELECT COUNT(DISTINCT visitor) FROM events WHERE kind='visit'"
            ).fetchone()[0]
            returning = db.execute(
                "SELECT COUNT(*) FROM (SELECT visitor FROM events WHERE kind='visit' "
                "GROUP BY visitor HAVING COUNT(DISTINCT substr(created_at,1,10)) > 1)"
            ).fetchone()[0]
            generated = db.execute(
                "SELECT COUNT(*) FROM events WHERE kind='generated'"
            ).fetchone()[0]
            cutoff = (datetime.now(UTC) - timedelta(days=7)).isoformat()
            recent = db.execute(
                "SELECT COUNT(DISTINCT visitor) FROM events WHERE kind='visit' AND created_at>=?",
                (cutoff,),
            ).fetchone()[0]
        return {
            "visits": visits,
            "visitors": visitors,
            "returning_visitors": returning,
            "retention_percent": round(returning / visitors * 100, 1) if visitors else 0.0,
            "generated": generated,
            "visitors_7d": recent,
        }


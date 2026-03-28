import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from .types import GeocodeEntry, Tournament

logger = logging.getLogger(__name__)


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def _transaction(conn: sqlite3.Connection) -> Generator[None, None, None]:
    try:
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def migrate(db_path: Path) -> None:
    """Create tables if they don't exist (idempotent)."""
    conn = _connect(db_path)
    with _transaction(conn):
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tournaments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT    NOT NULL,
                name        TEXT    NOT NULL,
                venue       TEXT    NOT NULL,
                prefecture  TEXT    NOT NULL,
                lat         REAL,
                lng         REAL,
                category    TEXT    NOT NULL,
                source_url  TEXT    NOT NULL,
                UNIQUE (date, name, venue)
            );

            CREATE TABLE IF NOT EXISTS geocode_cache (
                venue_name          TEXT    PRIMARY KEY,
                lat                 REAL,
                lng                 REAL,
                manually_corrected  INTEGER NOT NULL DEFAULT 0,
                updated_at          TEXT    NOT NULL
            );
        """)
    conn.close()
    logger.info("DB migration complete: %s", db_path)


def upsert_tournaments(db_path: Path, tournaments: list[Tournament]) -> int:
    """Insert tournaments, ignoring duplicates. Returns inserted count."""
    conn = _connect(db_path)
    count = 0
    with _transaction(conn):
        for t in tournaments:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO tournaments
                    (date, name, venue, prefecture, lat, lng, category, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    t.date.isoformat(),
                    t.name,
                    t.venue,
                    t.prefecture,
                    t.lat,
                    t.lng,
                    ",".join(t.categories),
                    t.source_url,
                ),
            )
            count += cur.rowcount
    conn.close()
    return count


def get_geocode_cache(
    db_path: Path, venue_name: str
) -> Optional[GeocodeEntry]:
    conn = _connect(db_path)
    row = conn.execute(
        "SELECT * FROM geocode_cache WHERE venue_name = ?", (venue_name,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return GeocodeEntry(
        venue_name=row["venue_name"],
        lat=row["lat"],
        lng=row["lng"],
        manually_corrected=bool(row["manually_corrected"]),
    )


def upsert_geocode_cache(db_path: Path, entry: GeocodeEntry) -> None:
    conn = _connect(db_path)
    with _transaction(conn):
        conn.execute(
            """
            INSERT INTO geocode_cache (venue_name, lat, lng, manually_corrected, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(venue_name) DO UPDATE SET
                lat                = excluded.lat,
                lng                = excluded.lng,
                manually_corrected = excluded.manually_corrected,
                updated_at         = excluded.updated_at
            WHERE manually_corrected = 0
            """,
            (
                entry.venue_name,
                entry.lat,
                entry.lng,
                int(entry.manually_corrected),
                datetime.utcnow().isoformat(),
            ),
        )
    conn.close()

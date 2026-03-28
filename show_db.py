"""data/shogi.db の中身を確認するスクリプト。"""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/shogi.db")


def show(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row

    # テーブル一覧
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    ]
    print(f"tables: {tables}\n")

    # tournaments
    total, = conn.execute("SELECT COUNT(*) FROM tournaments").fetchone()
    with_coords, = conn.execute(
        "SELECT COUNT(*) FROM tournaments WHERE lat IS NOT NULL"
    ).fetchone()
    print(f"=== tournaments  ({total} rows, {with_coords} with lat/lng) ===")

    print("\n--- prefecture breakdown ---")
    for row in conn.execute(
        "SELECT prefecture, COUNT(*) AS cnt FROM tournaments GROUP BY prefecture ORDER BY cnt DESC"
    ):
        print(f"  {row['prefecture']}: {row['cnt']}")

    print("\n--- sample (10 rows) ---")
    for row in conn.execute(
        "SELECT date, prefecture, name, venue, lat, lng FROM tournaments ORDER BY date LIMIT 10"
    ):
        coords = f"({row['lat']:.4f}, {row['lng']:.4f})" if row["lat"] else "no coords"
        print(f"  {row['date']} [{row['prefecture']}] {row['name']} / {row['venue']} {coords}")

    # geocode_cache
    cache_total, = conn.execute("SELECT COUNT(*) FROM geocode_cache").fetchone()
    manual, = conn.execute(
        "SELECT COUNT(*) FROM geocode_cache WHERE manually_corrected = 1"
    ).fetchone()
    print(f"\n=== geocode_cache  ({cache_total} rows, {manual} manually corrected) ===")
    for row in conn.execute(
        "SELECT venue_name, lat, lng, manually_corrected, updated_at FROM geocode_cache ORDER BY updated_at DESC LIMIT 10"
    ):
        flag = " [manual]" if row["manually_corrected"] else ""
        coords = f"({row['lat']:.4f}, {row['lng']:.4f})" if row["lat"] else "no coords"
        print(f"  {row['venue_name']} {coords}{flag}  updated={row['updated_at']}")


if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        raise SystemExit(1)
    conn = sqlite3.connect(DB_PATH)
    try:
        show(conn)
    finally:
        conn.close()

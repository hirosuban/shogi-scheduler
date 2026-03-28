import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.config import ApiConfig
from src.api.main import create_app


def _prepare_test_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE tournaments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT    NOT NULL,
                name        TEXT    NOT NULL,
                venue       TEXT    NOT NULL,
                prefecture  TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                source_url  TEXT    NOT NULL,
                UNIQUE (date, name, venue)
            );
            """
        )
        conn.executemany(
            """
            INSERT INTO tournaments (date, name, venue, prefecture, category, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "2026-04-10",
                    "A Tournament",
                    "Shinjuku",
                    "東京都",
                    "一般",
                    "https://example.com/a",
                ),
                (
                    "2026-05-12",
                    "B Tournament",
                    "Yokohama",
                    "神奈川県",
                    "一般,女流",
                    "https://example.com/b",
                ),
                (
                    "2026-06-15",
                    "C Tournament",
                    "Kawasaki",
                    "神奈川県",
                    "小学生",
                    "https://example.com/c",
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def _build_client(db_path: Path) -> TestClient:
    app = create_app(
        ApiConfig(
            db_path=db_path,
            frontend_origins=("http://localhost:5173",),
        )
    )
    return TestClient(app)


def test_get_tournaments_returns_summary_list(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _prepare_test_db(db_path)
    client = _build_client(db_path)

    response = client.get("/tournaments")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["name"] == "A Tournament"
    assert "lat" not in payload[0]
    assert "lng" not in payload[0]
    assert "source_url" not in payload[0]


def test_get_tournaments_filters_are_applied(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _prepare_test_db(db_path)
    client = _build_client(db_path)

    response = client.get(
        "/tournaments",
        params=[
            ("prefecture", "神奈川県"),
            ("from", "2026-05-01"),
            ("to", "2026-05-31"),
            ("category", "女流"),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "B Tournament"


def test_get_tournament_detail_and_not_found(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _prepare_test_db(db_path)
    client = _build_client(db_path)

    ok = client.get("/tournaments/1")
    not_found = client.get("/tournaments/999")

    assert ok.status_code == 200
    assert ok.json()["source_url"] == "https://example.com/a"
    assert not_found.status_code == 404

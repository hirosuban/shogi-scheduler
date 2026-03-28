import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .types import TournamentDetail, TournamentFilters, TournamentSummary


class TournamentRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def list_tournaments(self, filters: TournamentFilters) -> list[TournamentSummary]:
        query = (
            "SELECT id, date, name, venue, prefecture, category "
            "FROM tournaments WHERE 1=1"
        )
        params: list[object] = []

        if filters.prefectures:
            placeholders = ",".join("?" for _ in filters.prefectures)
            query += f" AND prefecture IN ({placeholders})"
            params.extend(filters.prefectures)

        if filters.date_from:
            query += " AND date >= ?"
            params.append(filters.date_from.isoformat())

        if filters.date_to:
            query += " AND date <= ?"
            params.append(filters.date_to.isoformat())

        if filters.category:
            # category is stored as comma-separated tokens; match exact token.
            query += " AND instr(',' || category || ',', ',' || ? || ',') > 0"
            params.append(filters.category)

        query += " ORDER BY date ASC, id ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        return [TournamentSummary.model_validate(dict(row)) for row in rows]

    def get_tournament(self, tournament_id: int) -> TournamentDetail | None:
        query = (
            "SELECT id, date, name, venue, prefecture, category, source_url "
            "FROM tournaments WHERE id = ?"
        )

        with self._connect() as conn:
            row = conn.execute(query, (tournament_id,)).fetchone()

        if row is None:
            return None

        return TournamentDetail.model_validate(dict(row))

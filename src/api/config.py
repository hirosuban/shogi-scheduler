import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ApiConfig:
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("TOURNAMENT_DB_PATH", "data/shogi.db"))
    )
    frontend_origins: tuple[str, ...] = field(
        default_factory=lambda: _parse_origins(
            os.getenv(
                "FRONTEND_ORIGINS",
                "http://localhost:5173,http://localhost:3000",
            )
        )
    )


def _parse_origins(raw: str) -> tuple[str, ...]:
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return tuple(origins)

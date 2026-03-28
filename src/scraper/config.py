from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    source_url: str = (
        "https://sho-shogi.blogspot.com/p/blog-page_20.html?m=1"
    )
    db_path: Path = field(default_factory=lambda: Path("data/shogi.db"))
    nominatim_user_agent: str = "shogi-scheduler/1.0"
    nominatim_delay_seconds: float = 1.1  # Nominatim rate limit: 1 req/sec
    kanto_prefectures: frozenset[str] = field(
        default_factory=lambda: frozenset(
            ["東京都", "神奈川県", "埼玉県", "千葉県"]
        )
    )
    schedule_interval_hours: int = 24


CONFIG = Config()

from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, ConfigDict


@dataclass(frozen=True)
class TournamentFilters:
    prefectures: tuple[str, ...] = ()
    date_from: date | None = None
    date_to: date | None = None
    category: str | None = None


class TournamentSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    date: date
    name: str
    venue: str
    prefecture: str
    category: str


class TournamentDetail(TournamentSummary):
    source_url: str

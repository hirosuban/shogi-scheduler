from .repository import TournamentRepository
from .types import TournamentDetail, TournamentFilters, TournamentSummary


class TournamentService:
    def __init__(self, repository: TournamentRepository) -> None:
        self._repository = repository

    def list_tournaments(self, filters: TournamentFilters) -> list[TournamentSummary]:
        return self._repository.list_tournaments(filters)

    def get_tournament(self, tournament_id: int) -> TournamentDetail | None:
        return self._repository.get_tournament(tournament_id)

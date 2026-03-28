from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import ApiConfig
from .repository import TournamentRepository
from .service import TournamentService
from .types import TournamentDetail, TournamentFilters, TournamentSummary


def create_app(config: ApiConfig | None = None) -> FastAPI:
    settings = config or ApiConfig()
    service = TournamentService(TournamentRepository(settings.db_path))

    app = FastAPI(title="Shogi Tournaments API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.frontend_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/tournaments", response_model=list[TournamentSummary])
    def get_tournaments(
        prefecture: list[str] | None = Query(default=None),
        from_date: date | None = Query(default=None, alias="from"),
        to_date: date | None = Query(default=None, alias="to"),
        category: str | None = Query(default=None, min_length=1),
    ) -> list[TournamentSummary]:
        filters = TournamentFilters(
            prefectures=tuple(prefecture or ()),
            date_from=from_date,
            date_to=to_date,
            category=category,
        )
        return service.list_tournaments(filters)

    @app.get("/tournaments/{tournament_id}", response_model=TournamentDetail)
    def get_tournament_detail(tournament_id: int) -> TournamentDetail:
        tournament = service.get_tournament(tournament_id)
        if tournament is None:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return tournament

    return app


app = create_app()

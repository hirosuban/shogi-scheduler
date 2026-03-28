import logging

from .config import Config
from .geocoder import attach_coordinates
from .parser import filter_kanto, scrape
from .repository import migrate, upsert_tournaments

logger = logging.getLogger(__name__)


def run_pipeline(config: Config) -> None:
    """Full pipeline: scrape → filter → geocode → save."""
    migrate(config.db_path)

    try:
        all_tournaments = scrape(config)
    except ValueError as exc:
        logger.error("Scraping failed (structure change detected): %s", exc)
        raise
    except Exception as exc:
        logger.error("Scraping failed (network/parse error): %s", exc)
        raise

    kanto = filter_kanto(all_tournaments, config)
    if not kanto:
        logger.warning("No Kanto tournaments found — possible data issue")

    with_coords = attach_coordinates(kanto, config)

    inserted = upsert_tournaments(config.db_path, with_coords)
    logger.info(
        "Pipeline complete: %d new records inserted (total processed: %d)",
        inserted,
        len(with_coords),
    )

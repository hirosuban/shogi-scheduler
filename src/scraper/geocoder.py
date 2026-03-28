import logging
import time
from pathlib import Path
from typing import Optional

from geopy.geocoders import Nominatim

from .config import Config
from .repository import get_geocode_cache, upsert_geocode_cache
from .types import GeocodeEntry, Tournament

logger = logging.getLogger(__name__)


def _geocode_nominatim(
    geolocator: Nominatim,
    venue: str,
    delay: float,
) -> tuple[Optional[float], Optional[float]]:
    try:
        time.sleep(delay)
        location = geolocator.geocode(venue, language="ja", timeout=10)
        if location:
            return location.latitude, location.longitude
    except Exception as exc:
        logger.warning("Nominatim error for %r: %s", venue, exc)
    return None, None


def attach_coordinates(
    tournaments: list[Tournament],
    config: Config,
) -> list[Tournament]:
    """Attach lat/lng to each tournament using cache + Nominatim fallback."""
    db_path: Path = config.db_path
    geolocator = Nominatim(user_agent=config.nominatim_user_agent)

    results: list[Tournament] = []
    for t in tournaments:
        entry = get_geocode_cache(db_path, t.venue)

        if entry is None:
            lat, lng = _geocode_nominatim(
                geolocator, t.venue, config.nominatim_delay_seconds
            )
            entry = GeocodeEntry(venue_name=t.venue, lat=lat, lng=lng)
            upsert_geocode_cache(db_path, entry)
            logger.debug(
                "Geocoded %r -> (%s, %s)", t.venue, lat, lng
            )
        else:
            logger.debug("Cache hit for %r", t.venue)

        results.append(
            Tournament(
                date=t.date,
                name=t.name,
                venue=t.venue,
                prefecture=t.prefecture,
                categories=t.categories,
                source_url=t.source_url,
                lat=entry.lat,
                lng=entry.lng,
            )
        )

    return results

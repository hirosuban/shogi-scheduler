import html
import json
import logging
import re
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .config import Config
from .types import Tournament

logger = logging.getLogger(__name__)

_JSON_PAT = re.compile(r"JSON\.parse\('(.+?)'\)", re.DOTALL)


def _fetch_html(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def _extract_events(html_text: str) -> list[dict]:
    """Extract the embedded JSON event array from the page."""
    m = _JSON_PAT.search(html_text)
    if not m:
        raise ValueError(
            "JSON event data not found in page — structure may have changed"
        )
    raw = html.unescape(m.group(1))
    return json.loads(raw)


def _parse_date(year: str, month: str, day: str) -> Optional[date]:
    try:
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        return None


def _detect_prefecture(event: dict) -> Optional[str]:
    """Return the prefecture string from additionalCategory, or None."""
    for cat in event.get("additionalCategory", []):
        # additionalCategory contains prefecture names like "東京都"
        if cat.endswith(("都", "道", "府", "県")):
            return cat
    return None


def scrape(config: Config) -> list[Tournament]:
    """Fetch and parse tournaments from the source URL.

    Returns all parsed entries regardless of prefecture filtering.
    Raises ValueError if the page structure is unrecognisable.
    """
    logger.info("Fetching %s", config.source_url)
    raw_html = _fetch_html(config.source_url)

    soup = BeautifulSoup(raw_html, "lxml")
    # Validate that expected markers are still present
    if not soup.find(id="event_lists") and "event_lists" not in raw_html:
        logger.warning(
            "Expected element #event_lists not found — "
            "page structure may have changed"
        )

    events = _extract_events(raw_html)
    logger.info("Parsed %d raw events", len(events))

    results: list[Tournament] = []
    for event in events:
        d = _parse_date(
            event.get("eventYear"),
            event.get("eventMonth"),
            event.get("eventDay"),
        )
        if d is None:
            logger.debug("Skipping event with invalid date: %s", event)
            continue

        prefecture = _detect_prefecture(event)
        if prefecture is None:
            logger.debug("No prefecture found for event: %s", event)
            continue

        results.append(
            Tournament(
                date=d,
                name=event.get("eventName", ""),
                venue=event.get("place", ""),
                prefecture=prefecture,
                categories=event.get("category", []),
                source_url=event.get("link", config.source_url),
            )
        )

    return results


def filter_kanto(
    tournaments: list[Tournament], config: Config
) -> list[Tournament]:
    """Keep only tournaments in the Kanto target prefectures."""
    filtered = [
        t for t in tournaments if t.prefecture in config.kanto_prefectures
    ]
    logger.info(
        "Kanto filter: %d/%d tournaments", len(filtered), len(tournaments)
    )
    return filtered

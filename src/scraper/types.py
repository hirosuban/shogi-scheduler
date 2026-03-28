from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Tournament:
    date: date
    name: str
    venue: str
    prefecture: str
    categories: list[str]
    source_url: str
    lat: Optional[float] = None
    lng: Optional[float] = None


@dataclass
class GeocodeEntry:
    venue_name: str
    lat: Optional[float]
    lng: Optional[float]
    manually_corrected: bool = False

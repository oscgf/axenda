from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    MUSICA = "Música"
    TEATRO = "Teatro"
    EXPOSICION = "Exposición"
    CINE = "Cine"
    DANZA = "Danza"
    LITERATURA = "Literatura"
    INFANTIL = "Infantil"
    OTROS = "Otros"


class City(BaseModel):
    id: int
    name: str
    region: str
    timezone: str = "Europe/Madrid"
    default_locale: str = "es"


class Venue(BaseModel):
    id: int
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    city_id: int


class Event(BaseModel):
    id: int
    title: str
    event_type: EventType
    description: str | None = None
    date_start: datetime
    date_end: datetime | None = None
    price_info: str | None = None
    url: str | None = None
    source: str
    source_id: str
    image_url: str | None = None
    venue_id: int | None = None
    city_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    venue: Venue | None = None
    genres: list[str] = Field(default_factory=list)

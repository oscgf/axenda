from abc import ABC, abstractmethod
from datetime import datetime

from axenda.domain.models import City, Event, EventType, Venue


class EventRepository(ABC):
    @abstractmethod
    async def search(
        self,
        city: str,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        event_type: EventType | None = None,
        genre: str | None = None,
        venue: str | None = None,
        limit: int = 10,
    ) -> list[Event]:
        ...

    @abstractmethod
    async def get_by_id(self, event_id: int) -> Event | None:
        ...

    @abstractmethod
    async def upsert(self, event: Event) -> Event:
        ...

    @abstractmethod
    async def find_by_source(self, source: str, source_id: str) -> Event | None:
        ...

    @abstractmethod
    async def count_by_city(self, city: str) -> int:
        ...


class VenueRepository(ABC):
    @abstractmethod
    async def list_by_city(self, city: str) -> list[Venue]:
        ...

    @abstractmethod
    async def get_or_create(self, name: str, city_id: int, address: str | None = None) -> Venue:
        ...

    @abstractmethod
    async def get_by_id(self, venue_id: int) -> Venue | None:
        ...


class CityRepository(ABC):
    @abstractmethod
    async def get_by_name(self, name: str) -> City | None:
        ...

    @abstractmethod
    async def get_or_create(
        self,
        name: str,
        region: str = "",
        timezone: str = "Europe/Madrid",
        default_locale: str = "es",
    ) -> City:
        ...

from datetime import datetime

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from axenda.domain.models import City, Event, EventType, Venue
from axenda.domain.repositories import CityRepository, EventRepository, VenueRepository
from axenda.infrastructure.database.orm_models import (
    CityModel,
    EventModel,
    GenreModel,
    VenueModel,
)


class SQLCityRepository(CityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_name(self, name: str) -> City | None:
        result = await self._session.execute(
            select(CityModel).where(CityModel.name.ilike(name))
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_or_create(
        self,
        name: str,
        region: str = "",
        timezone: str = "Europe/Madrid",
        default_locale: str = "es",
    ) -> City:
        existing = await self.get_by_name(name)
        if existing:
            return existing
        model = CityModel(
            name=name, region=region, timezone=timezone, default_locale=default_locale
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: CityModel) -> City:
        return City(
            id=model.id,
            name=model.name,
            region=model.region,
            timezone=model.timezone,
            default_locale=model.default_locale,
        )


class SQLVenueRepository(VenueRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_city(self, city: str) -> list[Venue]:
        result = await self._session.execute(
            select(VenueModel)
            .join(CityModel)
            .where(CityModel.name.ilike(city))
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_or_create(
        self, name: str, city_id: int, address: str | None = None
    ) -> Venue:
        result = await self._session.execute(
            select(VenueModel).where(
                VenueModel.name == name, VenueModel.city_id == city_id
            )
        )
        model = result.scalar_one_or_none()
        if model:
            if address and model.address != address:
                model.address = address
                await self._session.flush()
            return self._to_domain(model)

        model = VenueModel(name=name, city_id=city_id, address=address)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def get_by_id(self, venue_id: int) -> Venue | None:
        result = await self._session.execute(
            select(VenueModel).where(VenueModel.id == venue_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: VenueModel) -> Venue:
        return Venue(
            id=model.id,
            name=model.name,
            address=model.address,
            latitude=model.latitude,
            longitude=model.longitude,
            city_id=model.city_id,
        )


class SQLEventRepository(EventRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        stmt = (
            select(EventModel)
            .join(CityModel)
            .options(
                selectinload(EventModel.venue),
                selectinload(EventModel.genres),
            )
            .where(CityModel.name.ilike(city))
        )

        if date_from:
            stmt = stmt.where(EventModel.date_start >= date_from)
        if date_to:
            stmt = stmt.where(
                (EventModel.date_end == None) | (EventModel.date_end <= date_to)  # noqa: E711
            )
            stmt = stmt.where(EventModel.date_start <= date_to)  # noqa: E711
        if event_type:
            stmt = stmt.where(EventModel.event_type == event_type.value)
        if genre:
            stmt = stmt.where(EventModel.genres.any(GenreModel.name == genre))
        if venue:
            stmt = stmt.where(VenueModel.name.ilike(f"%{venue}%"))

        stmt = stmt.order_by(EventModel.date_start.asc()).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.unique().scalars().all()]

    async def get_by_id(self, event_id: int) -> Event | None:
        result = await self._session.execute(
            select(EventModel)
            .options(selectinload(EventModel.venue), selectinload(EventModel.genres))
            .where(EventModel.id == event_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def upsert(self, event: Event) -> Event:
        model = EventModel(
            title=event.title,
            event_type=event.event_type.value,
            description=event.description,
            date_start=event.date_start,
            date_end=event.date_end,
            price_info=event.price_info,
            url=event.url,
            source=event.source,
            source_id=event.source_id,
            image_url=event.image_url,
            venue_id=event.venue_id,
            city_id=event.city_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        event.id = model.id
        event.created_at = model.created_at
        event.updated_at = model.updated_at
        return event

    async def find_by_source(self, source: str, source_id: str) -> Event | None:
        result = await self._session.execute(
            select(EventModel)
            .options(selectinload(EventModel.venue), selectinload(EventModel.genres))
            .where(
                EventModel.source == source,
                EventModel.source_id == source_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def count_by_city(self, city: str) -> int:
        result = await self._session.execute(
            select(EventModel).join(CityModel).where(CityModel.name == city)
        )
        return len(result.scalars().all())

    @staticmethod
    def _to_domain(model: EventModel) -> Event:
        venue = None
        if model.venue_id is not None:
            state = inspect(model)
            if "venue" not in state.unloaded and model.venue is not None:
                venue = Venue(
                    id=model.venue.id,
                    name=model.venue.name,
                    address=model.venue.address,
                    latitude=model.venue.latitude,
                    longitude=model.venue.longitude,
                    city_id=model.venue.city_id,
                )

        return Event(
            id=model.id,
            title=model.title,
            event_type=EventType(model.event_type),
            description=model.description,
            date_start=model.date_start,
            date_end=model.date_end,
            price_info=model.price_info,
            url=model.url,
            source=model.source,
            source_id=model.source_id,
            image_url=model.image_url,
            venue_id=model.venue_id,
            city_id=model.city_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            venue=venue,
            genres=[g.name for g in model.genres],
        )

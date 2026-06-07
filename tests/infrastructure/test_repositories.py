from datetime import UTC, datetime

import pytest
from axenda.domain.models import Event, EventType
from axenda.infrastructure.database.orm_models import Base
from axenda.infrastructure.database.repositories import (
    SQLCityRepository,
    SQLEventRepository,
    SQLVenueRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s

    await engine.dispose()


@pytest.mark.asyncio
async def test_city_get_or_create(session: AsyncSession) -> None:
    repo = SQLCityRepository(session)
    city = await repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")
    assert city.name == "Gijón"
    assert city.id > 0

    same = await repo.get_or_create(name="Gijón", name_normalized="gijon")
    assert same.id == city.id


@pytest.mark.asyncio
async def test_city_get_by_name_not_found(session: AsyncSession) -> None:
    repo = SQLCityRepository(session)
    city = await repo.get_by_name("NoExiste")
    assert city is None


@pytest.mark.asyncio
async def test_venue_get_or_create(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    venue_repo = SQLVenueRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")
    venue = await venue_repo.get_or_create(
        name="Teatro Jovellanos", city_id=city.id, address="Calle A"
    )
    assert venue.id > 0
    assert venue.name == "Teatro Jovellanos"

    same = await venue_repo.get_or_create(name="Teatro Jovellanos", city_id=city.id)
    assert same.id == venue.id


@pytest.mark.asyncio
async def test_venue_list_by_city(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    venue_repo = SQLVenueRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")
    await venue_repo.get_or_create(name="Sala A", city_id=city.id)
    await venue_repo.get_or_create(name="Sala B", city_id=city.id)

    venues = await venue_repo.list_by_city("Gijón")
    assert len(venues) == 2


@pytest.mark.asyncio
async def test_event_upsert_and_find(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    event = Event(
        id=0,
        title="Concierto de prueba",
        event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 1, 21, 0, tzinfo=UTC),
        source="test",
        source_id="evt-001",
        city_id=city.id,
    )
    saved = await event_repo.upsert(event)
    assert saved.id > 0

    found = await event_repo.find_by_source("test", "evt-001")
    assert found is not None
    assert found.title == "Concierto de prueba"


@pytest.mark.asyncio
async def test_event_search_by_city(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    await event_repo.upsert(Event(
        id=0, title="Evento 1", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 5, tzinfo=UTC),
        source="test", source_id="e1", city_id=city.id,
    ))
    await event_repo.upsert(Event(
        id=0, title="Evento 2", event_type=EventType.TEATRO,
        event_date=datetime(2026, 6, 10, tzinfo=UTC),
        source="test", source_id="e2", city_id=city.id,
    ))

    results = await event_repo.search(city="Gijón", limit=10)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_event_search_by_type(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    await event_repo.upsert(Event(
        id=0, title="Concierto", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 5, tzinfo=UTC),
        source="test", source_id="m1", city_id=city.id,
    ))
    await event_repo.upsert(Event(
        id=0, title="Obra de teatro", event_type=EventType.TEATRO,
        event_date=datetime(2026, 6, 10, tzinfo=UTC),
        source="test", source_id="t1", city_id=city.id,
    ))

    results = await event_repo.search(city="Gijón", event_type=EventType.MUSICA, limit=10)
    assert len(results) == 1
    assert results[0].event_type == EventType.MUSICA


@pytest.mark.asyncio
async def test_event_search_by_date_range(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    await event_repo.upsert(Event(
        id=0, title="Evento junio", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 5, tzinfo=UTC),
        source="test", source_id="d1", city_id=city.id,
    ))
    await event_repo.upsert(Event(
        id=0, title="Evento julio", event_type=EventType.MUSICA,
        event_date=datetime(2026, 7, 5, tzinfo=UTC),
        source="test", source_id="d2", city_id=city.id,
    ))

    results = await event_repo.search(
        city="Gijón",
        date_from=datetime(2026, 6, 1, tzinfo=UTC),
        date_to=datetime(2026, 6, 30, tzinfo=UTC),
        limit=10,
    )
    assert len(results) == 1
    assert results[0].title == "Evento junio"


@pytest.mark.asyncio
async def test_event_count_by_city(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    await event_repo.upsert(Event(
        id=0, title="E1", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 1, tzinfo=UTC),
        source="t", source_id="c1", city_id=city.id,
    ))
    await event_repo.upsert(Event(
        id=0, title="E2", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 2, tzinfo=UTC),
        source="t", source_id="c2", city_id=city.id,
    ))

    count = await event_repo.count_by_city("Gijón")
    assert count == 2


@pytest.mark.asyncio
async def test_event_deduplication(session: AsyncSession) -> None:
    city_repo = SQLCityRepository(session)
    event_repo = SQLEventRepository(session)

    city = await city_repo.get_or_create(name="Gijón", name_normalized="gijon", region="Asturias")

    await event_repo.upsert(Event(
        id=0, title="Único", event_type=EventType.MUSICA,
        event_date=datetime(2026, 6, 1, tzinfo=UTC),
        source="test", source_id="unique-1", city_id=city.id,
    ))

    found = await event_repo.find_by_source("test", "unique-1")
    assert found is not None

    count = await event_repo.count_by_city("Gijón")
    assert count == 1

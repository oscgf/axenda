import asyncio
from datetime import UTC, datetime

from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import ScrapeLogModel
from axenda.infrastructure.database.repositories import (
    SQLCityRepository,
    SQLEventRepository,
    SQLVenueRepository,
)
from axenda.infrastructure.scraper.registry import get_scrapers


async def run_scraper(scraper) -> None:
    log = ScrapeLogModel(
        source=scraper.source,
        status="running",
        started_at=datetime.now(UTC),
    )

    try:
        raw_data = scraper.fetch()
        events = scraper.parse(raw_data)
        events_found = len(raw_data)

        async with async_session() as session:
            city_repo = SQLCityRepository(session)
            venue_repo = SQLVenueRepository(session)
            event_repo = SQLEventRepository(session)

            city = await city_repo.get_or_create(
                name=scraper.city_name,
                region="Asturias",
            )

            events_new = 0
            events_updated = 0

            for event in events:
                event.city_id = city.id

                raw_item = _find_raw_item(raw_data, event.source_id)
                if raw_item:
                    venue_name = scraper.get_venue_name(raw_item)
                    if venue_name:
                        venue_addr = scraper.get_venue_address(raw_item) or None
                        venue = await venue_repo.get_or_create(
                            name=venue_name,
                            city_id=city.id,
                            address=venue_addr,
                        )
                        event.venue_id = venue.id

                existing = await event_repo.find_by_source(event.source, event.source_id)
                if existing:
                    events_updated += 1
                else:
                    await event_repo.upsert(event)
                    events_new += 1

            await session.commit()

            log.status = "success"
            log.events_found = events_found
            log.events_new = events_new
            log.events_updated = events_updated
            log.finished_at = datetime.now(UTC)
            session.add(log)
            await session.commit()

    except Exception as exc:
        async with async_session() as session:
            log.status = "error"
            log.error_message = str(exc)
            log.finished_at = datetime.now(UTC)
            session.add(log)
            await session.commit()
        raise


def _find_raw_item(raw_data: list[dict], source_id: str) -> dict | None:
    for item in raw_data:
        if str(item.get("id", "")) == source_id:
            return item
    return None


def main() -> None:
    scrapers = get_scrapers()
    for scraper in scrapers:
        print(f"Running scraper: {scraper.source}")
        asyncio.run(run_scraper(scraper))
        print(f"Done: {scraper.source}")


if __name__ == "__main__":
    main()

"""Resumen general: eventos, ciudades, venues, logs."""
import asyncio
from sqlalchemy import select, func
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import (
    EventModel,
    CityModel,
    VenueModel,
    ScrapeLogModel,
)


async def main():
    async with async_session() as s:
        events = (await s.execute(select(func.count(EventModel.id)))).scalar()
        cities = (await s.execute(select(func.count(CityModel.id)))).scalar()
        venues = (await s.execute(select(func.count(VenueModel.id)))).scalar()
        logs = (await s.execute(select(func.count(ScrapeLogModel.id)))).scalar()
        print(f"Eventos: {events}  |  Ciudades: {cities}  |  Venues: {venues}  |  Logs: {logs}")


if __name__ == "__main__":
    asyncio.run(main())

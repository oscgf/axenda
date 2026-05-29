"""Venues con más eventos."""
import asyncio
from sqlalchemy import select, func
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import EventModel, VenueModel


async def main():
    async with async_session() as s:
        result = await s.execute(
            select(VenueModel.name, func.count(EventModel.id))
            .join(EventModel.venue)
            .group_by(VenueModel.name)
            .order_by(func.count(EventModel.id).desc())
            .limit(10)
        )
        for name, count in result:
            print(f"  {name}: {count} eventos")


if __name__ == "__main__":
    asyncio.run(main())

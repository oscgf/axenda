"""Tipos de evento y cuántos hay de cada."""
import asyncio
from sqlalchemy import select, func
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import EventModel


async def main():
    async with async_session() as s:
        result = await s.execute(
            select(EventModel.event_type, func.count()).group_by(EventModel.event_type)
        )
        for tipo, count in result:
            print(f"  {tipo}: {count}")


if __name__ == "__main__":
    asyncio.run(main())

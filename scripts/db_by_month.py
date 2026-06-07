"""Distribución de eventos por mes."""
import asyncio
from sqlalchemy import select, func, extract
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import EventModel


async def main():
    async with async_session() as s:
        result = await s.execute(
            select(extract("month", EventModel.event_date), func.count())
            .group_by(extract("month", EventModel.event_date))
            .order_by(extract("month", EventModel.event_date))
        )
        meses = [
            "", "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        ]
        for m, c in result:
            print(f"  {meses[int(m)]}: {c} eventos")


if __name__ == "__main__":
    asyncio.run(main())

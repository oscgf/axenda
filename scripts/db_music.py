"""Últimos eventos de música y rango de fechas."""
import asyncio
from datetime import UTC, datetime
from sqlalchemy import select, func
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import EventModel


async def main():
    async with async_session() as s:
        min_max = await s.execute(
            select(func.min(EventModel.date_start), func.max(EventModel.date_start))
        )
        mn, mx = min_max.one()
        print(f"Rango de fechas: {mn.strftime('%d/%m/%Y')} → {mx.strftime('%d/%m/%Y')}")

        result = await s.execute(
            select(EventModel)
            .where(EventModel.event_type == "Música")
            .order_by(EventModel.date_start.desc())
            .limit(10)
        )
        print("\nÚltimos 10 eventos de MÚSICA:")
        for e in result.scalars():
            print(f"  [{e.date_start.strftime('%d/%m/%Y')}] {e.title[:70]}")

        count_future = await s.execute(
            select(func.count(EventModel.id)).where(
                EventModel.date_start >= datetime.now(UTC)
            )
        )
        print(f"\nEventos futuros: {count_future.scalar()}")


if __name__ == "__main__":
    asyncio.run(main())

"""Próximos N eventos (por fecha). Uso: python scripts/db_upcoming.py [N]"""
import asyncio
import sys
from datetime import UTC, datetime
from sqlalchemy import select
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.orm_models import EventModel


async def main(limit: int = 10):
    async with async_session() as s:
        result = await s.execute(
            select(EventModel)
            .where(EventModel.event_date >= datetime.now(UTC))
            .order_by(EventModel.event_date.asc())
            .limit(limit)
        )
        for e in result.scalars():
            print(f"  [{e.event_date.strftime('%d/%m')}] {e.title[:70]}  ({e.event_type})")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(main(limit))

"""Probar el flujo LLM → tool call → BD → respuesta."""
import asyncio
from axenda.infrastructure.config import settings
from axenda.infrastructure.database.engine import async_session
from axenda.infrastructure.database.repositories import (
    SQLEventRepository,
    SQLVenueRepository,
)
from axenda.infrastructure.llm.client import OllamaClient
from axenda.application.search_events import SearchEventsUseCase


async def main():
    llm = OllamaClient()
    async with async_session() as session:
        event_repo = SQLEventRepository(session)
        venue_repo = SQLVenueRepository(session)
        use_case = SearchEventsUseCase(llm, event_repo, venue_repo)

        queries = [
            "¿Qué conciertos hay este fin de semana en Gijón?",
            "Dime eventos de música en Gijón",
            "¿Qué teatros hay en Gijón?",
        ]

        for query in queries:
            print(f"\n{'='*60}")
            print(f"PREGUNTA: {query}")
            print(f"{'='*60}")
            try:
                answer = await use_case.execute(
                    query, city=settings.default_city
                )
                print(f"RESPUESTA: {answer[:500]}")
            except Exception as e:
                print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())

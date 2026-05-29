"""Chat interactivo con el LLM + tools + BD. Escribe 'salir' para terminar."""
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
    print("Axenda Chat — escribe 'salir' para terminar")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            break

        print("Axenda: ", end="", flush=True)

        async with async_session() as session:
            event_repo = SQLEventRepository(session)
            venue_repo = SQLVenueRepository(session)
            use_case = SearchEventsUseCase(llm, event_repo, venue_repo)

            answer = await use_case.execute(
                user_input, city=settings.default_city
            )
            print(answer)


if __name__ == "__main__":
    asyncio.run(main())

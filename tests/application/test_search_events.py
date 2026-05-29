from datetime import UTC, datetime

import pytest
from axenda.domain.models import Event, EventType


class FakeEventRepo:
    def __init__(self) -> None:
        self.events: list[Event] = []

    async def search(self, **kwargs) -> list[Event]:  # type: ignore[override]
        return self.events

    async def get_by_id(self, event_id: int) -> Event | None:  # type: ignore[override]
        return next((e for e in self.events if e.id == event_id), None)

    async def upsert(self, event: Event) -> Event:  # type: ignore[override]
        return event

    async def find_by_source(self, source: str, source_id: str) -> Event | None:  # type: ignore[override]
        return None

    async def count_by_city(self, city: str) -> int:  # type: ignore[override]
        return len(self.events)


class FakeVenueRepo:
    async def list_by_city(self, city: str) -> list:  # type: ignore[override]
        return []

    async def get_or_create(self, **kwargs) -> None:  # type: ignore[override]
        ...

    async def get_by_id(self, venue_id: int) -> None:  # type: ignore[override]
        ...


class FakeOllamaClient:
    def __init__(self, tool_name: str = "search_events", arguments: dict | None = None) -> None:
        self.tool_name = tool_name
        self.arguments = arguments or {"city": "Gijón"}
        self.calls: list[dict] = []

    def build_system_message(self, city: str, locale: str = "es") -> dict:
        return {"role": "system", "content": f"System {city} {locale}"}

    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        self.calls.append({"messages": messages, "tools": tools})
        if len(self.calls) == 1:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "function": {
                                "name": self.tool_name,
                                "arguments": self.arguments,
                            },
                        }
                    ],
                }
            }
        else:
            return {"message": {"role": "assistant", "content": "Aquí tienes los resultados."}}


@pytest.mark.asyncio
async def test_search_events_use_case_basic() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    llm = FakeOllamaClient(
        tool_name="search_events",
        arguments={"city": "Gijón", "event_type": "Música"},
    )
    events = FakeEventRepo()
    venues = FakeVenueRepo()

    events.events = [
        Event(
            id=1,
            title="Concierto de prueba",
            event_type=EventType.MUSICA,
            date_start=datetime(2026, 6, 1, tzinfo=UTC),
            source="test",
            source_id="1",
            city_id=1,
        )
    ]

    use_case = SearchEventsUseCase(llm, events, venues)
    result = await use_case.execute("¿Hay conciertos?", "Gijón")
    assert "resultados" in result.lower() or "Aquí" in result


@pytest.mark.asyncio
async def test_search_events_use_case_no_results() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    llm = FakeOllamaClient(tool_name="search_events", arguments={"city": "Gijón"})
    events = FakeEventRepo()
    venues = FakeVenueRepo()

    use_case = SearchEventsUseCase(llm, events, venues)
    result = await use_case.execute("¿Hay algo?", "Gijón")
    assert "resultados" in result.lower() or "Aquí" in result


@pytest.mark.asyncio
async def test_search_events_use_case_no_tool_call() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    class NoToolLLM(FakeOllamaClient):
        async def chat(self, messages, tools=None):
            return {"message": {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}}

    llm = NoToolLLM()
    events = FakeEventRepo()
    venues = FakeVenueRepo()

    use_case = SearchEventsUseCase(llm, events, venues)
    result = await use_case.execute("Hola", "Gijón")
    assert "Hola" in result


@pytest.mark.asyncio
async def test_parse_date_valid() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    uc = SearchEventsUseCase(None, None, None)  # type: ignore[arg-type]
    result = uc._parse_date("2026-06-15")
    assert result is not None
    assert result.year == 2026
    assert result.month == 6
    assert result.day == 15


@pytest.mark.asyncio
async def test_parse_date_invalid() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    uc = SearchEventsUseCase(None, None, None)  # type: ignore[arg-type]
    assert uc._parse_date("notadate") is None
    assert uc._parse_date(None) is None


@pytest.mark.asyncio
async def test_parse_event_type_valid() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    uc = SearchEventsUseCase(None, None, None)  # type: ignore[arg-type]
    assert uc._parse_event_type("Música") == EventType.MUSICA
    assert uc._parse_event_type("Teatro") == EventType.TEATRO


@pytest.mark.asyncio
async def test_parse_event_type_invalid() -> None:
    from axenda.application.search_events import SearchEventsUseCase

    uc = SearchEventsUseCase(None, None, None)  # type: ignore[arg-type]
    assert uc._parse_event_type("Fiestón") is None
    assert uc._parse_event_type(None) is None

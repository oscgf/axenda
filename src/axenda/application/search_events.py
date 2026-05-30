from datetime import datetime

from axenda.domain.models import EventType
from axenda.domain.repositories import EventRepository, VenueRepository
from axenda.infrastructure.llm.client import OllamaClient
from axenda.infrastructure.llm.tools import ALL_TOOLS


class SearchEventsUseCase:
    def __init__(
        self,
        llm: OllamaClient,
        event_repo: EventRepository,
        venue_repo: VenueRepository,
    ) -> None:
        self._llm = llm
        self._event_repo = event_repo
        self._venue_repo = venue_repo

    async def execute(self, user_query: str, city: str, locale: str = "es") -> str:
        system_msg = self._llm.build_system_message(city, locale)
        user_msg = {"role": "user", "content": user_query}

        response = await self._llm.chat(
            messages=[system_msg, user_msg],
            tools=ALL_TOOLS,
        )

        message = response["message"]

        if "tool_calls" not in message or not message["tool_calls"]:
            return message.get("content", "") or "Sin resultados."

        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        tool_result = await self._execute_tool(function_name, arguments, city)
        return self._format_result(function_name, tool_result)

    async def _execute_tool(
        self, name: str, arguments: dict, default_city: str
    ) -> dict:
        if name == "search_events":
            return await self._handle_search(arguments, default_city)
        elif name == "get_event_details":
            return await self._handle_details(arguments)
        elif name == "list_venues":
            return await self._handle_list_venues(arguments, default_city)
        else:
            return {"error": f"Unknown function: {name}"}

    async def _handle_search(self, args: dict, default_city: str) -> dict:
        city = _normalize_city(args.get("city", default_city))
        date_from = _parse_date(args.get("date_from"))
        date_to = _parse_date(args.get("date_to"))
        event_type = _parse_event_type(args.get("event_type"))
        genre = args.get("genre")
        venue = args.get("venue")
        limit = _parse_limit(args.get("limit", 10))

        events = await self._event_repo.search(
            city=city,
            date_from=date_from,
            date_to=date_to,
            event_type=event_type,
            genre=genre,
            venue=venue,
            limit=limit,
        )

        return {
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "event_type": e.event_type.value,
                    "date": e.date_start.strftime("%d/%m/%Y"),
                    "date_end": e.date_end.strftime("%d/%m/%Y") if e.date_end else None,
                    "venue": e.venue.name if e.venue else "Sin espacio",
                    "city": city,
                    "price_info": e.price_info or "Consultar",
                    "genres": e.genres,
                    "url": e.url or "",
                }
                for e in events
            ],
            "total": len(events),
            "city": city,
        }

    async def _handle_details(self, args: dict) -> dict:
        event_id = args.get("event_id")
        if not event_id:
            return {"error": "event_id requerido"}

        event = await self._event_repo.get_by_id(int(event_id))
        if not event:
            return {"error": f"No encontrado: {event_id}"}

        return {
            "id": event.id,
            "title": event.title,
            "event_type": event.event_type.value,
            "description": event.description,
            "date_start": event.date_start.strftime("%d/%m/%Y %H:%M"),
            "date_end": event.date_end.strftime("%d/%m/%Y %H:%M") if event.date_end else None,
            "venue": event.venue.name if event.venue else "Sin espacio",
            "price_info": event.price_info,
            "genres": event.genres,
            "url": event.url,
        }

    async def _handle_list_venues(self, args: dict, default_city: str) -> dict:
        city = _normalize_city(args.get("city", default_city))
        venues = await self._venue_repo.list_by_city(city)
        return {
            "venues": [
                {"id": v.id, "name": v.name, "address": v.address}
                for v in venues
            ],
            "city": city,
            "total": len(venues),
        }

    @staticmethod
    def _format_result(function_name: str, result: dict) -> str:
        if function_name == "list_venues":
            return _format_venues(result)
        elif function_name == "get_event_details":
            return _format_detail(result)
        else:
            return _format_events(result)


def _format_events(result: dict) -> str:
    events = result.get("events", [])
    total = result.get("total", 0)
    city = result.get("city", "")

    if not events:
        return f"No se encontraron eventos en {city}. Prueba con otras fechas o tipos."

    lines = [f"🎭 Eventos en {city} ({total} resultados):\n"]
    for e in events:
        line = (
            f"📅 {e['date']} — {e['title']} ({e['event_type']}) "
            f"— {e['venue']} — {e['price_info']}"
        )
        lines.append(line)
        if e.get("url"):
            lines.append(f"🔗 {e['url']}")
    lines.append("\nFuente: Ayuntamiento de Gijón")
    return "\n".join(lines)


def _format_venues(result: dict) -> str:
    venues = result.get("venues", [])
    city = result.get("city", "")

    if not venues:
        return f"No hay espacios registrados en {city}."

    lines = [f"📍 Espacios en {city}:\n"]
    for v in venues:
        addr = f" — {v['address']}" if v.get("address") else ""
        lines.append(f"• {v['name']}{addr}")
    return "\n".join(lines)


def _format_detail(result: dict) -> str:
    if "error" in result:
        return result["error"]

    lines = [
        f"🎭 {result['title']}",
        f"📅 {result['date_start']}",
    ]
    if result.get("venue"):
        lines.append(f"📍 {result['venue']}")
    if result.get("price_info"):
        lines.append(f"💰 {result['price_info']}")
    if result.get("description"):
        lines.append(f"\n{result['description']}")
    if result.get("url"):
        lines.append(f"\n🔗 {result['url']}")
    return "\n".join(lines)


def _normalize_city(name: str) -> str:
    accents = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    }
    for accented, plain in accents.items():
        name = name.replace(accented, plain)
    return name.lower()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def _parse_event_type(value: str | None) -> EventType | None:
    if not value:
        return None
    corrections = {
        "múmica": "Música", "músico": "Música", "musica": "Música",
        "teatral": "Teatro", "obras": "Teatro",
        "exposicion": "Exposición", "expos": "Exposición",
        "cinema": "Cine", "cines": "Cine",
    }
    value = corrections.get(value.lower().strip(), value)
    try:
        return EventType(value)
    except ValueError:
        return None


def _parse_limit(value) -> int:
    if isinstance(value, int):
        return max(1, value)
    if isinstance(value, str) and value.strip():
        try:
            return max(1, int(value))
        except (ValueError, TypeError):
            pass
    return 10

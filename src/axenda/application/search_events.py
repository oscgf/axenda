import json
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
            return message.get("content", "") or "No tengo información para responder a eso."

        tool_call = message["tool_calls"][0]
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        tool_result = await self._execute_tool(function_name, arguments, city)

        final_messages = [
            system_msg,
            user_msg,
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [tool_call],
            },
            {
                "role": "tool",
                "content": json.dumps(tool_result, ensure_ascii=False),
            },
        ]

        final_response = await self._llm.chat(messages=final_messages)
        return final_response["message"]["content"]

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
        city = self._normalize_city(args.get("city", default_city))
        date_from = self._parse_date(args.get("date_from"))
        date_to = self._parse_date(args.get("date_to"))
        event_type = self._parse_event_type(args.get("event_type"))
        genre = args.get("genre")
        venue = args.get("venue")
        limit = args.get("limit", 10)

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
            return {"error": "event_id is required"}

        event = await self._event_repo.get_by_id(event_id)
        if not event:
            return {"error": f"No event found with id {event_id}"}

        return {
            "id": event.id,
            "title": event.title,
            "event_type": event.event_type.value,
            "description": event.description,
            "date_start": event.date_start.isoformat(),
            "date_end": event.date_end.isoformat() if event.date_end else None,
            "venue": event.venue.name if event.venue else None,
            "price_info": event.price_info,
            "genres": event.genres,
            "url": event.url,
        }

    async def _handle_list_venues(self, args: dict, default_city: str) -> dict:
        city = self._normalize_city(args.get("city", default_city))
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
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _parse_event_type(value: str | None) -> EventType | None:
        if not value:
            return None
        try:
            return EventType(value)
        except ValueError:
            return None

    @staticmethod
    def _normalize_city(name: str) -> str:
        accents = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        }
        for accented, plain in accents.items():
            name = name.replace(accented, plain)
        return name.lower()

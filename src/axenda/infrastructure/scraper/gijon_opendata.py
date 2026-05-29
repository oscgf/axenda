import hashlib
from datetime import UTC, datetime
from html import unescape

import httpx

from axenda.domain.models import Event, EventType
from axenda.infrastructure.scraper.base import BaseScraper

API_URL = "https://opendata.gijon.es/descargar.php?id=728&tipo=JSON"


class GijonOpenDataScraper(BaseScraper):
    source = "gijon_opendata"
    city_name = "Gijón"

    def __init__(self) -> None:
        self._min_date = datetime(2026, 1, 1, tzinfo=UTC)

    def fetch(self) -> list[dict]:
        response = httpx.get(API_URL, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def parse(self, raw: list[dict]) -> list[Event]:
        events: list[Event] = []
        found_any = False
        for item in raw:
            try:
                event = self._parse_event(item)
                if event:
                    events.append(event)
                    found_any = True
            except Exception:
                continue

        if not found_any and self._min_date.year > 2025:
            self._min_date = datetime(2025, 1, 1, tzinfo=UTC)
            return self.parse(raw)

        return events

    def get_source_id(self, raw_event: dict) -> str:
        raw_id = raw_event.get("id", "")
        if raw_id:
            return str(raw_id)
        title = raw_event.get("titulo", "")
        date_str = self._parse_date_str(raw_event.get("fecha_inicio", ""))
        venue = raw_event.get("titulo_directorio", "")
        fingerprint = f"{title}|{date_str}|{venue}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]

    def _parse_event(self, item: dict) -> Event | None:
        title = self._clean_html(item.get("titulo", ""))
        if not title:
            return None

        event_type_str = item.get("tipo", "Otros")
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            event_type = EventType.OTROS

        date_start = self._parse_date(item.get("fecha_inicio", ""))

        if date_start < self._min_date:
            return None

        date_end = self._parse_date(item.get("fecha_fin", ""), first_line=True)
        if date_end and date_end.date() == date_start.date():
            date_end = None

        url = self._clean_url(item.get("alias", ""))

        return Event(
            id=0,
            title=title,
            event_type=event_type,
            description=None,
            date_start=date_start,
            date_end=date_end,
            price_info=None,
            url=url,
            source=self.source,
            source_id=self.get_source_id(item),
            image_url=self._clean_url(item.get("imagen", "")),
            city_id=0,
            venue_id=None,
            venue=None,
        )

    def get_venue_name(self, raw_event: dict) -> str:
        return raw_event.get("titulo_directorio", "") or ""

    def get_venue_address(self, raw_event: dict) -> str:
        return raw_event.get("direccion_directorio", "") or ""

    @staticmethod
    def _clean_html(text: str) -> str:
        if not text:
            return ""
        text = unescape(text)
        text = text.replace("&quot;", '"').replace("&#039;", "'").replace("&amp;", "&")
        text = text.replace("\n", " ").strip()
        return text

    @staticmethod
    def _parse_date_str(date_str: str) -> str:
        if not date_str:
            return ""
        return date_str.split("\n")[0].strip()

    @staticmethod
    def _parse_date(date_str: str, first_line: bool = True) -> datetime:
        if not date_str:
            raise ValueError("Empty date string")

        lines = date_str.strip().split("\n")
        raw = lines[0].strip() if first_line else lines[-1].strip()

        raw = raw.split(" - ")[-1].strip()

        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse date: {raw}")

    @staticmethod
    def _clean_url(url: str) -> str:
        if not url:
            return ""
        return url.strip()

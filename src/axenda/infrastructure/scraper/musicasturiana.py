import re
from datetime import UTC, datetime
from html import unescape

import httpx

from axenda.domain.models import Event, EventType
from axenda.infrastructure.scraper.base import BaseScraper

API_URL_EVENTS = "https://musicasturiana.com/wp-json/tribe/events/v1/events"
API_URL_VENUES = "https://musicasturiana.com/wp-json/tribe/events/v1/venues"

"""
    {
      "id": 49295,
      "global_id": "musicasturiana.com?id=49295",
      "global_id_lineage": [
        "musicasturiana.com?id=49295"
      ],
      "author": "279",
      "status": "publish",
      "date": "2026-04-01 15:13:00",
      "date_utc": "2026-04-01 15:13:00",
      "modified": "2026-05-15 09:30:40",
      "modified_utc": "2026-05-15 09:30:40",
      "url": "https://musicasturiana.com/evento/maria-trubia-y-pau-santirso-en-santo-adriano/",
      "rest_url": "https://musicasturiana.com/wp-json/tribe/events/v1/events/49295",
      "title": "María Trubia y Pau Santirso en Santu Adrianu",
      "description": "\u003Cp\u003EMaría Trubia y Pau Santirso, con destacaes trayectories nel ámbitu de la música y el baille tradicional asturianu, presenten un espectáculu participativu dirixíu a tolos públicos. La propuesta pon en valor el patrimoniu cultural al traviés del usu de panderos, cantu y baille, fomentando la implicación activa de los asistentes.\u003C/p\u003E\n\u003Cp\u003EMientres l’actuación, el públicu podrá deprender y acompañar diverses melodíes tradicionales. Una iniciativa qu&#8217;axunta tradición y divulgación cultural nun formatu accesible y dinámicu.\u003C/p\u003E",
      "excerpt": "\u003Cp\u003EEstes destacaes persones nel ámbitu de la música y el baille tradicional asturianu ufren un conciertu que pon en valor el patrimoniu cultural al traviés del usu de panderos, cantu y baille, fomentando la implicación activa de los asistentes.\u003C/p\u003E",
      "slug": "maria-trubia-y-pau-santirso-en-santo-adriano",
      "image": {
        "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez.jpg",
        "id": 39630,
        "extension": "jpg",
        "width": 1200,
        "height": 600,
        "filesize": 108858,
        "sizes": {
          "medium": {
            "width": 300,
            "height": 150,
            "mime-type": "image/jpeg",
            "filesize": 13216,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-300x150.jpg"
          },
          "large": {
            "width": 1024,
            "height": 512,
            "mime-type": "image/jpeg",
            "filesize": 83356,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-1024x512.jpg"
          },
          "thumbnail": {
            "width": 150,
            "height": 150,
            "mime-type": "image/jpeg",
            "filesize": 7013,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-150x150.jpg"
          },
          "medium_large": {
            "width": 768,
            "height": 384,
            "mime-type": "image/jpeg",
            "filesize": 54394,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-768x384.jpg"
          },
          "woocommerce_thumbnail": {
            "width": 1000,
            "height": 600,
            "mime-type": "image/jpeg",
            "filesize": 98795,
            "uncropped": false,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-1000x600.jpg"
          },
          "woocommerce_single": {
            "width": 1000,
            "height": 500,
            "mime-type": "image/jpeg",
            "filesize": 81414,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-1000x500.jpg"
          },
          "woocommerce_gallery_thumbnail": {
            "width": 100,
            "height": 100,
            "mime-type": "image/jpeg",
            "filesize": 4095,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-100x100.jpg"
          },
          "variation_swatches_image_size": {
            "width": 50,
            "height": 50,
            "mime-type": "image/jpeg",
            "filesize": 1848,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-50x50.jpg"
          },
          "variation_swatches_tooltip_size": {
            "width": 100,
            "height": 100,
            "mime-type": "image/jpeg",
            "filesize": 4095,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-100x100.jpg"
          },
          "dgwt-wcas-product-suggestion": {
            "width": 64,
            "height": 32,
            "mime-type": "image/jpeg",
            "filesize": 1563,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-64x32.jpg"
          },
          "cmplz_banner_image": {
            "width": 350,
            "height": 100,
            "mime-type": "image/jpeg",
            "filesize": 10450,
            "url": "https://musicasturiana.com/wp-content/uploads/2025/05/pau-santirso-y-maria-vazquez-350x100.jpg"
          }
        }
      },
      "all_day": false,
      "start_date": "2026-06-07 12:00:00",
      "start_date_details": {
        "year": "2026",
        "month": "06",
        "day": "07",
        "hour": "12",
        "minutes": "00",
        "seconds": "00"
      },
      "end_date": "2026-06-07 13:00:00",
      "end_date_details": {
        "year": "2026",
        "month": "06",
        "day": "07",
        "hour": "13",
        "minutes": "00",
        "seconds": "00"
      },
      "utc_start_date": "2026-06-07 12:00:00",
      "utc_start_date_details": {
        "year": "2026",
        "month": "06",
        "day": "07",
        "hour": "12",
        "minutes": "00",
        "seconds": "00"
      },
      "utc_end_date": "2026-06-07 13:00:00",
      "utc_end_date_details": {
        "year": "2026",
        "month": "06",
        "day": "07",
        "hour": "13",
        "minutes": "00",
        "seconds": "00"
      },
      "timezone": "UTC+0",
      "timezone_abbr": "UTC+0",
      "cost": "",
      "cost_details": {
        "currency_symbol": "€",
        "currency_code": "EUR",
        "currency_position": "suffix",
        "values": []
      },
      "website": "",
      "show_map": true,
      "show_map_link": true,
      "hide_from_listings": false,
      "sticky": false,
      "featured": false,
      "categories": [
        {
          "name": "Folk / Celta / Tradicional",
          "slug": "folk-celta-tradicional",
          "term_group": 0,
          "term_taxonomy_id": 881,
          "taxonomy": "tribe_events_cat",
          "description": "",
          "parent": 0,
          "count": 386,
          "filter": "raw",
          "id": 881,
          "urls": {
            "self": "https://musicasturiana.com/wp-json/tribe/events/v1/categories/881",
            "collection": "https://musicasturiana.com/wp-json/tribe/events/v1/categories"
          }
        }
      ],
      "tags": [],
      "venue": {
        "id": 49296,
        "author": "279",
        "status": "publish",
        "date": "2026-04-01 15:13:00",
        "date_utc": "2026-04-01 15:13:00",
        "modified": "2026-04-01 15:13:00",
        "modified_utc": "2026-04-01 15:13:00",
        "url": "https://musicasturiana.com/recinto/santo-adriano/",
        "venue": "Santo Adriano",
        "slug": "santo-adriano",
        "zip": "33115",
        "show_map": true,
        "show_map_link": true,
        "global_id": "musicasturiana.com?id=49296",
        "global_id_lineage": [
          "musicasturiana.com?id=49296"
        ]
      },
      "organizer": [],
      "custom_fields": []
    },
"""


class MusicasturianaScraper(BaseScraper):
    source = "musicasturiana"
    city_region = "Asturias"

    def __init__(self) -> None:
        self._venues_by_id: dict[int, dict] = {}

    def fetch(self) -> list[dict]:
        all_events: list[dict] = []
        url: str | None = API_URL_EVENTS
        params: dict = {
            "per_page": 50,  # Maximum allowed by API
            "status": "publish",
        }

        while url is not None:
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            events = data.get("events", [])
            all_events.extend(events)
            url = data.get("next_rest_url")  # Next page URL from API with pagination params
            params = {}  # Clear params for next page to avoid pagination issues

        self._venues_by_id = self._fetch_venues()
        return all_events

    def _fetch_venues(self) -> dict[int, dict]:
        """Obtiene todos los venues desde API_URL_VENUES y los indexa por id.

        El endpoint de venues expone campos que el objeto embebido en cada
        evento no incluye (city, address, state, country), necesarios para
        resolver la ciudad y la dirección de cada evento.
        """
        venues_by_id: dict[int, dict] = {}
        url: str | None = API_URL_VENUES
        params: dict = {"per_page": 50}

        while url is not None:
            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            for venue in data.get("venues", []):
                venue_id = venue.get("id")
                if venue_id is not None:
                    venues_by_id[int(venue_id)] = venue
            url = data.get("next_rest_url")
            params = {}

        return venues_by_id

    def _resolve_venue(self, raw_event: dict) -> dict:
        """Devuelve el venue completo desde API_URL_VENUES o el embebido como fallback."""
        embedded = raw_event.get("venue")
        if not isinstance(embedded, dict):
            return {}
        venue_id = embedded.get("id")
        if venue_id is None:
            return embedded
        return self._venues_by_id.get(int(venue_id), embedded)

    def get_venue_name(self, raw_event: dict) -> str:
        venue = self._resolve_venue(raw_event)
        return venue.get("venue", "") or ""

    def get_venue_address(self, raw_event: dict) -> str:
        venue = self._resolve_venue(raw_event)
        parts = []
        if venue.get("address"):
            parts.append(venue["address"])
        if venue.get("city"):
            parts.append(venue["city"])
        if venue.get("state"):
            parts.append(venue["state"])
        return ", ".join(parts)

    def get_venue_url(self, raw_event: dict) -> str:
        venue = self._resolve_venue(raw_event)
        return venue.get("url", "") or ""

    def get_event_city_name(self, raw_event: dict) -> str:
        """Devuelve el nombre de la ciudad del evento desde la API de venues."""
        venue = self._resolve_venue(raw_event)
        return venue.get("city", "") or ""

    def _parse_event(self, item: dict) -> Event | None:
        """Parsea un evento individual desde un diccionario crudo.

        Args:
            item: Diccionario con datos del evento de la API.

        Returns:
            Objeto Event o None si el evento no es válido.
        """

        return Event(
            id=0,
            title=unescape(item.get("title", "")) or None,
            event_type=EventType.MUSICA,
            description=self._clean_html(item.get("description", "")) or None,
            event_date=self._parse_date(item.get("start_date", "")),
            price_info=item.get("cost", "") or None,
            url=item.get("url", ""),
            source=self.source,
            source_id=self.get_source_id(item),
            image_url=(item.get("image") or {}).get("url", "") or None,
            city_id=0,
            venue_id=None,
        )

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        if not date_str:
            raise ValueError("Empty date string")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)

import hashlib
from datetime import UTC, datetime
from html import unescape

import httpx

from axenda.domain.models import Event, EventType
from axenda.infrastructure.scraper.base import BaseScraper

API_URL = "https://drupal.gijon.es/es/listado_eventos_tes4/?_format=json"

"""Scraper para eventos del Ayuntamiento de Gijón (Drupal Open Data).

Obtiene eventos desde la API JSON de Gijón y los convierte al modelo de dominio.

Data example:

{
    "titulo": "Música. !Que viva México¡ Coro infantil de Gijón.",
    "materia": "Cultural",
    "distrito": "Llano",
    "tipo": "Música",
    "edad_maxima": "",
    "edad_minima": "",
    "imagen": (
        "/sites/default/files/styles/imagen_4_3/public/2026-05/CORO%20INFANTIL_0.jpg"
        "?h=3cfb2c93&amp;itok=dmnjk1kX "
    ),
    "tipo_publico": "General",
    "field_localizacion_en_el_directo": "159",
    "field_video_youtube": "",
    "thumbnail__alt": "SE OBSERVA IMAGEN DEL CORO INFANTIL DE GIJÓN",
    "organismo": "Ayuntamiento",
    "programa": "",
    "esDestacado": "",
    "localizaciones": "159",
    "alias_directorio": "/centro-municipal-integrado-el-llano",
    "titulo_directorio": "Centro Municipal Integrado El Llano",
    "direccion_directorio": "Calle Río de Oro, 37",
    "etiquetas": "Música",
    "field_lo_name": "",
    "field_lo_url": "",
    "field_lo_address": "",
    "hora_inicio": "19:00",
    "fecha_inicio": "2026-06-03",
    "hora_fin": "",
    "fecha_fin": "2026-06-03",
    "fechas": "2026-06-03",
    "id": "41464",
    "alias": "/musica-que-viva-mexico-coro-infantil-de-gijon",
    "peso": "0",
    "field_estado_del_evento": "",
    "field_area": ""
}
"""

class GijonOpenDataScraper(BaseScraper):
    """Scraper de eventos del portal Drupal de Gijón.

    Extrae eventos de la API pública del Ayuntamiento de Gijón y los normaliza
    al modelo de dominio Event.
    """
    source = "gijon_drupal"
    city_region = "Asturias"

    def fetch(self) -> list[dict]:
        response = httpx.get(API_URL, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def get_event_city_name(self, raw_event: dict) -> str:
        return "Gijón"

    def get_venue_name(self, raw_event: dict) -> str:
        return raw_event.get("titulo_directorio", "") or ""

    def get_venue_address(self, raw_event: dict) -> str:
        """Extrae la dirección del lugar del evento.

        Args:
            raw_event: Diccionario con datos crudos del evento.

        Returns:
            Dirección del lugar o string vacío si no está disponible.
        """
        return raw_event.get("direccion_directorio", "") or ""

    def get_venue_url(self, raw_event: dict) -> str:
        """Extrae la URL del lugar del evento.

        Args:
            raw_event: Diccionario con datos crudos del evento.

        Returns:
            URL del lugar o string vacío si no está disponible.
        """
        return self._clean_url(raw_event.get("alias_directorio", ""), endpoint="directorio")

    def _parse_event(self, item: dict) -> Event | None:
        """Parsea un evento individual desde un diccionario crudo.

        Args:
            item: Diccionario con datos del evento de la API.

        Returns:
            Objeto Event o None si el evento no es válido.
        """

        return Event(
            id=0,
            title=self._clean_html(item.get("titulo", "")) or None,
            event_type=self._parse_event_type(item.get("tipo", "Otros")),
            description=None,
            event_date=self._parse_date(item.get("fecha_inicio", "")),
            price_info=None,
            url=self._clean_url(item.get("alias", ""), endpoint="eventos"),
            source=self.source,
            source_id=self.get_source_id(item),
            image_url=self._clean_url(item.get("imagen", "")),
            city_id=0,
            venue_id=None,
        )

    @staticmethod
    def _parse_event_type(event_type_str: str) -> EventType:
        """Parsea el tipo de evento desde una cadena.
        
        Args:
            event_type_str: Cadena con el tipo de evento.
            
        Returns:
            EventType correspondiente o EventType.OTROS si no se encuentra.
        """
        try:
            return EventType(event_type_str)
        except ValueError:
            return EventType.OTROS

    @staticmethod
    def _parse_date_str(date_str: str) -> str:
        """Extrae la primera línea de una cadena de fecha.

        Args:
            date_str: Cadena de fecha potencialmente multilínea.

        Returns:
            Primera línea de la fecha o string vacío.
        """
        if not date_str:
            return ""
        return date_str.split("\n")[0].strip()

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parsea una cadena de fecha a datetime con zona horaria UTC.

        Soporta múltiples formatos: ISO 8601, datetime completo y DD/MM/YYYY.

        Args:
            date_str: Cadena de fecha a parsear.
            first_line: Si True, usa la primera línea; si False, la última.

        Returns:
            Objeto datetime con zona horaria UTC.

        Raises:
            ValueError: Si la cadena está vacía o no se puede parsear.
        """
        if not date_str:
            raise ValueError("Empty date string")

        raw = date_str.strip().split("\n")[0].strip()

        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse date: {raw}")

    @staticmethod
    def _clean_url(
        alias: str,
        endpoint: str | None = None,
    ) -> str:
        """Construye la URL completa del evento desde su alias.

        Args:
            alias: Alias o path del evento (ej: "/musica-concierto").

        Returns:
            URL completa del evento o string vacío si no hay alias.
        """
        if not alias:
            return ""
        slug = alias.strip().lstrip("/")
        base_url: str = "https://www.gijon.es"
        return f"{base_url}/{endpoint}/{slug}" if endpoint else f"{base_url}/{slug}"

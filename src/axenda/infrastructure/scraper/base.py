import hashlib
import re
from abc import ABC, abstractmethod
from html import unescape

from axenda.domain.models import Event
from axenda.domain.text import _normalize_city


class BaseScraper(ABC):
    source: str
    city_region: str = ""

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Obtiene los eventos crudos desde la API.

        Returns:
            Lista de diccionarios con los datos de eventos en formato JSON.
        """
        ...

    def parse(self, raw: list[dict]) -> list[Event]:
        """Convierte los datos crudos en objetos Event.

        Args:
            raw: Lista de diccionarios con datos de eventos de la API.

        Returns:
            Lista de objetos Event parseados. Los eventos inválidos se ignoran.
        """
        events: list[Event] = []
        for item in raw:
            try:
                event = self._parse_event(item)
                if event:
                    events.append(event)
            except Exception:
                continue
        return events

    def get_source_id(self, raw_event: dict, id_field: str = "id") -> str:
        """Genera un identificador único para el evento desde la fuente.

        Usa el campo especificado por `id_field` concatenado con el nombre de la fuente
        y genera un hash a partir de ahí.

        Args:
            raw_event: Diccionario con datos crudos del evento.
            id_field: Nombre del campo que contiene el ID en la fuente.

        Returns:
            Identificador único como string.
        """
        raw_id = raw_event.get(id_field, "")
        fingerprint = f"{raw_id}|{self.source}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]

    @abstractmethod
    def get_venue_name(self, raw_event: dict) -> str:
        """Extrae el nombre del lugar del evento.

        Args:
            raw_event: Diccionario con datos crudos del evento.

        Returns:
            Nombre del lugar o string vacío si no está disponible.
        """
        ...

    @abstractmethod
    def get_event_city_name(self, raw_event: dict) -> str:
        """Devuelve el nombre de la ciudad del evento en el idioma de la fuente.

        Para scrapers de una sola ciudad, devuelve siempre el mismo nombre.
        Para scrapers multi-ciudad (agregadores, ticketeras), devuelve la
        ciudad de cada evento a partir de los datos de origen.
        """
        ...

    def get_event_city_normalized(self, raw_event: dict) -> str:
        """Devuelve la ciudad normalizada (minúsculas, sin acentos).

        Implementación por defecto: normaliza el resultado de
        ``get_event_city_name``. Sobrescribir si la fuente requiere una
        limpieza previa antes de normalizar.
        """
        return _normalize_city(self.get_event_city_name(raw_event))

    @staticmethod
    def _clean_html(text: str) -> str:
        """Limpia entidades HTML y normaliza el texto.

        Args:
            text: Texto con posibles entidades HTML.

        Returns:
            Texto limpio sin entidades HTML ni saltos de línea.
        """
        if not text:
            return ""
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = text.replace("&quot;", '"').replace("&#039;", "'").replace("&amp;", "&")
        text = text.replace("&#8211;", "-").replace("&#8217;", "'")
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
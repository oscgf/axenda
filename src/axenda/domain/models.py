"""Modelos de dominio para la aplicación Axenda.

Define las entidades principales del sistema: EventType, City, Venue y Event.
Estos modelos son puros y no dependen de la infraestructura.
"""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeración de tipos de eventos.

    Define las categorías principales de eventos culturales y de entretenimiento.
    """
    MUSICA = "Música"
    TEATRO = "Teatro"
    EXPOSICION = "Exposición"
    CINE = "Cine"
    DANZA = "Danza"
    LITERATURA = "Literatura"
    INFANTIL = "Infantil"
    OTROS = "Otros"


class City(BaseModel):
    """Representa una ciudad donde se celebran eventos.

    Attributes:
        id: Identificador único de la ciudad.
        name: Nombre de la ciudad.
        name_normalized: Nombre de la ciudad normalizado (minúsculas, sin acentos).
        region: Región o provincia donde se encuentra la ciudad.
        timezone: Zona horaria de la ciudad (por defecto Europe/Madrid).
        default_locale: Idioma por defecto (por defecto es).
    """
    id: int
    name: str
    name_normalized: str
    region: str
    timezone: str = "Europe/Madrid"
    default_locale: str = "es"


class Venue(BaseModel):
    """Representa un lugar o recinto donde se celebran eventos.

    Attributes:
        id: Identificador único del lugar.
        name: Nombre del lugar.
        address: Dirección física del lugar.
        url: URL del lugar (opcional).
        city_id: Identificador de la ciudad donde se encuentra el lugar.
    """
    id: int
    name: str
    address: str | None = None
    url: str | None = None
    city_id: int


class Event(BaseModel):
    """Representa un evento cultural o de entretenimiento.

    Attributes:
        id: Identificador único del evento en la base de datos.
        title: Título del evento.
        event_type: Tipo o categoría del evento.
        description: Descripción detallada del evento.
        event_date: Fecha y hora de inicio del evento.
        price_info: Información sobre precios o entrada.
        url: URL del evento en la fuente original.
        source: Nombre de la fuente de datos (ej: gijon_drupal).
        source_id: Identificador del evento en la fuente original.
        image_url: URL de la imagen del evento.
        venue_id: Identificador del lugar donde se celebra el evento.
        city_id: Identificador de la ciudad del evento.
        created_at: Timestamp de creación del registro.
        updated_at: Timestamp de última actualización del registro.
        genres: Lista de géneros o etiquetas del evento.
    """
    id: int
    title: str
    event_type: EventType
    description: str | None = None
    event_date: datetime
    price_info: str | None = None
    url: str | None = None
    source: str
    source_id: str
    image_url: str | None = None
    venue_id: int | None = None
    city_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    genres: list[str] = Field(default_factory=list)

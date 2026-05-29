from abc import ABC, abstractmethod

from axenda.domain.models import Event


class BaseScraper(ABC):
    source: str
    city_name: str

    @abstractmethod
    def fetch(self) -> list[dict]:
        ...

    @abstractmethod
    def parse(self, raw: list[dict]) -> list[Event]:
        ...

    @abstractmethod
    def get_source_id(self, raw_event: dict) -> str:
        ...

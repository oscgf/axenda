from axenda.infrastructure.scraper.base import BaseScraper
from axenda.infrastructure.scraper.gijon_opendata import GijonOpenDataScraper


def get_scrapers() -> list[BaseScraper]:
    return [
        GijonOpenDataScraper(),
    ]

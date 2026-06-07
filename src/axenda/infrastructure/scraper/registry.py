from axenda.infrastructure.scraper.base import BaseScraper
from axenda.infrastructure.scraper.gijon_opendata import GijonOpenDataScraper
from axenda.infrastructure.scraper.musicasturiana import MusicasturianaScraper


def get_scrapers() -> list[BaseScraper]:
    return [
        GijonOpenDataScraper(),
        MusicasturianaScraper(),
    ]

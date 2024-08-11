from typing import Protocol, TypeVar

ScrapeResult = TypeVar("ScrapeResult", covariant=True)


class BaseScraper(Protocol[ScrapeResult]):
    def scrape(self) -> ScrapeResult: ...

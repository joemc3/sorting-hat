import httpx
import trafilatura


class ScraperError(Exception):
    pass


class Scraper:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def fetch_and_extract(self, url: str) -> tuple[str, str]:
        """Fetch URL and extract main content. Returns (raw_html, extracted_text)."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, follow_redirects=True
            ) as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (compatible; SortingHat/1.0; "
                            "+https://github.com/sorting-hat)"
                        )
                    },
                )
                response.raise_for_status()
                raw_html = response.text
        except httpx.HTTPError as e:
            raise ScraperError(f"Failed to fetch {url}: {e}") from e

        extracted = trafilatura.extract(
            raw_html,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
        )

        if not extracted:
            raise ScraperError(f"Could not extract meaningful content from {url}")

        return raw_html, extracted

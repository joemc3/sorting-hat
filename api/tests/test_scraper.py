import trafilatura

from sorting_hat.services.scraper import Scraper, ScraperError


def test_scraper_exists():
    scraper = Scraper()
    assert scraper.timeout == 30.0


def test_scraper_custom_timeout():
    scraper = Scraper(timeout=10.0)
    assert scraper.timeout == 10.0


def test_scraper_error_is_exception():
    assert issubclass(ScraperError, Exception)


def test_trafilatura_extracts_content():
    """Verify trafilatura can extract content from a simple HTML page."""
    html = """
    <html>
    <head><title>Test Product</title></head>
    <body>
        <nav>Navigation here</nav>
        <main>
            <h1>Amazing Security Product</h1>
            <p>Our endpoint protection platform defends your devices against
            malware, ransomware, and advanced threats using AI-powered detection.</p>
            <p>Features include real-time scanning, behavioral analysis,
            and automated response capabilities.</p>
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """
    result = trafilatura.extract(html, include_comments=False, favor_recall=True)
    assert result is not None
    assert "endpoint protection" in result.lower() or "security" in result.lower()

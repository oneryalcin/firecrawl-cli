import pytest
from firecrawl_cli.utils import url_to_filename, get_api_key


def test_url_to_filename_basic():
    """Convert basic URL to filename slug."""
    result = url_to_filename("https://example.com/page")
    assert result == "example-com-page.md"


def test_url_to_filename_with_path():
    """Convert URL with multiple path segments."""
    result = url_to_filename("https://docs.firecrawl.dev/features/scrape")
    assert result == "docs-firecrawl-dev-features-scrape.md"


def test_url_to_filename_root():
    """Convert root URL."""
    result = url_to_filename("https://example.com")
    assert result == "example-com.md"


def test_url_to_filename_with_query():
    """Remove query params from filename."""
    result = url_to_filename("https://example.com/page?foo=bar")
    assert result == "example-com-page.md"


def test_get_api_key_success(monkeypatch):
    """Get API key from environment."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
    result = get_api_key()
    assert result == "fc-test-key"


def test_get_api_key_missing(monkeypatch):
    """Raise error when API key missing."""
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    with pytest.raises(ValueError, match="FIRECRAWL_API_KEY"):
        get_api_key()

"""Utility functions for firecrawl CLI."""
import os
import re
from urllib.parse import urlparse


def url_to_filename(url: str) -> str:
    """Convert URL to filesystem-safe filename.

    Args:
        url: Full URL to convert

    Returns:
        Slugified filename with .md extension

    Example:
        >>> url_to_filename("https://example.com/page")
        "example-com-page.md"
    """
    parsed = urlparse(url)

    # Get domain without www
    domain = parsed.netloc.replace("www.", "")

    # Get path without leading/trailing slashes
    path = parsed.path.strip("/")

    # Combine domain and path
    if path:
        full_slug = f"{domain}/{path}"
    else:
        full_slug = domain

    # Replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', full_slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return f"{slug}.md"


def get_api_key() -> str:
    """Get Firecrawl API key from environment.

    Returns:
        API key string

    Raises:
        ValueError: If FIRECRAWL_API_KEY not set
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError(
            "FIRECRAWL_API_KEY environment variable not set.\n"
            "Get your API key from https://firecrawl.dev and run:\n"
            "export FIRECRAWL_API_KEY='fc-your-api-key'"
        )
    return api_key

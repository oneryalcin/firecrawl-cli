# Firecrawl CLI

CLI tool for [Firecrawl API](https://firecrawl.dev) - map, scrape, crawl, and batch operations.

## Installation

Install globally with uv:

```bash
uv tool install .
```

Or install in editable mode for development:

```bash
uv pip install -e .
```

## Setup

Get your API key from [firecrawl.dev](https://firecrawl.dev) and set it:

```bash
export FIRECRAWL_API_KEY='fc-your-api-key'
```

## Usage

### Map - Get all URLs from a website

```bash
# Basic usage
firecrawl map https://example.com

# Limit results
firecrawl map https://example.com --limit 50

# Search for specific URLs
firecrawl map https://example.com --search docs
```

### Scrape - Single page

```bash
# Output to stdout
firecrawl scrape https://example.com

# Save to file
firecrawl scrape https://example.com -o output.md
```

### Crawl - Recursive website crawling

```bash
# Output to stdout
firecrawl crawl https://example.com

# Save to directory (creates multiple files)
firecrawl crawl https://example.com --limit 10 -o output/

# Each page saved as: domain-slug-page.md
```

### Batch - Multiple URLs

```bash
# From command line
firecrawl batch https://example.com/page1 https://example.com/page2 -o output/

# From file (one URL per line)
firecrawl batch --source urls.txt -o output/
```

## Development

Run tests:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src/firecrawl_cli
```

## License

MIT

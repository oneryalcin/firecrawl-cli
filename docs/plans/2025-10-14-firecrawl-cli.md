# Firecrawl CLI Implementation Plan

> **For Claude:** Use `${SUPERPOWERS_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Build a CLI tool for Firecrawl API supporting map, scrape, crawl, and batch operations with markdown output.

**Architecture:** Typer-based CLI with subcommands. Each command wraps Firecrawl SDK calls. Utility module handles URL-to-filename conversion and API client initialization. Output to stdout by default, files for batch (-o required) and optionally for scrape/crawl.

**Tech Stack:** Python, uv, Typer, firecrawl-py

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/firecrawl_cli/__init__.py`
- Create: `src/firecrawl_cli/cli.py`
- Create: `tests/__init__.py`

**Step 1: Initialize uv project**

Run:
```bash
cd /Users/mehmetoneryalcin/dev/personal/firecrawl-cli
uv init --lib
```

Expected: Creates basic project structure

**Step 2: Write pyproject.toml**

Create `pyproject.toml`:
```toml
[project]
name = "firecrawl-cli"
version = "0.1.0"
description = "CLI tool for Firecrawl API"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "firecrawl-py>=1.0.0",
    "typer>=0.12.0",
]

[project.scripts]
firecrawl = "firecrawl_cli.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]
```

**Step 3: Create package structure**

Run:
```bash
mkdir -p src/firecrawl_cli tests
touch src/firecrawl_cli/__init__.py tests/__init__.py
```

Expected: Directory structure created

**Step 4: Verify uv sync**

Run:
```bash
uv sync
```

Expected: Dependencies installed successfully

---

## Task 2: Utility Functions

**Files:**
- Create: `src/firecrawl_cli/utils.py`
- Create: `tests/test_utils.py`

**Step 1: Write failing test for url_to_filename**

Create `tests/test_utils.py`:
```python
import pytest
from firecrawl_cli.utils import url_to_filename


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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_utils.py -v`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

Create `src/firecrawl_cli/utils.py`:
```python
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_utils.py -v`
Expected: PASS - all tests pass

**Step 5: Write test for get_api_key**

Add to `tests/test_utils.py`:
```python
from firecrawl_cli.utils import get_api_key


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
```

**Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_utils.py::test_get_api_key_success -v`
Expected: PASS

**Step 7: Commit**

Run:
```bash
git add src/firecrawl_cli/utils.py tests/test_utils.py pyproject.toml src/firecrawl_cli/__init__.py tests/__init__.py
git commit -m "feat: add project setup and utility functions"
```

---

## Task 3: CLI Main App and Map Command

**Files:**
- Create: `src/firecrawl_cli/cli.py`
- Create: `src/firecrawl_cli/commands/__init__.py`
- Create: `src/firecrawl_cli/commands/map.py`
- Create: `tests/test_map.py`

**Step 1: Write test for map command**

Create `tests/test_map.py`:
```python
from unittest.mock import Mock, patch
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_map_basic(monkeypatch):
    """Map command outputs URLs to stdout."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_client = Mock()
    mock_client.map.return_value = {
        "links": [
            {"url": "https://example.com/page1", "title": "Page 1"},
            {"url": "https://example.com/page2", "title": "Page 2"},
        ]
    }

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["map", "https://example.com"])

    assert result.exit_code == 0
    assert "https://example.com/page1" in result.stdout
    assert "https://example.com/page2" in result.stdout
    assert "Page 1" in result.stdout


def test_map_with_limit(monkeypatch):
    """Map command respects limit parameter."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_client = Mock()
    mock_client.map.return_value = {"links": []}

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["map", "https://example.com", "--limit", "50"])

    mock_client.map.assert_called_once_with(
        url="https://example.com",
        limit=50,
        search=None
    )
    assert result.exit_code == 0


def test_map_with_search(monkeypatch):
    """Map command supports search parameter."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_client = Mock()
    mock_client.map.return_value = {"links": []}

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["map", "https://example.com", "--search", "docs"])

    mock_client.map.assert_called_once_with(
        url="https://example.com",
        limit=None,
        search="docs"
    )
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_map.py -v`
Expected: FAIL - modules not found

**Step 3: Create CLI main app**

Create `src/firecrawl_cli/cli.py`:
```python
"""Main CLI application."""
import typer
from typing import Optional


app = typer.Typer(
    name="firecrawl",
    help="CLI tool for Firecrawl API - map, scrape, crawl, and batch operations",
    no_args_is_help=True,
)


# Commands will be registered here
from firecrawl_cli.commands import map as map_cmd

app.command(name="map")(map_cmd.map_command)


if __name__ == "__main__":
    app()
```

**Step 4: Implement map command**

Create `src/firecrawl_cli/commands/__init__.py`:
```python
"""Command modules."""
```

Create `src/firecrawl_cli/commands/map.py`:
```python
"""Map command implementation."""
import typer
from typing import Optional
from firecrawl import Firecrawl
from firecrawl_cli.utils import get_api_key


def map_command(
    url: str = typer.Argument(..., help="URL to map"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Maximum number of links to return"),
    search: Optional[str] = typer.Option(None, "--search", help="Search for specific URLs"),
):
    """Get all URLs from a website (fast)."""
    try:
        api_key = get_api_key()
        firecrawl = Firecrawl(api_key=api_key)

        # Call map API
        result = firecrawl.map(url=url, limit=limit, search=search)

        # Output results to stdout
        links = result.get("links", [])

        if not links:
            typer.echo("No links found.")
            return

        typer.echo(f"Found {len(links)} links:\n")

        for link in links:
            url = link.get("url", "")
            title = link.get("title", "")

            if title:
                typer.echo(f"{url} - {title}")
            else:
                typer.echo(url)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_map.py -v`
Expected: PASS - all tests pass

**Step 6: Test CLI manually**

Run: `uv run firecrawl map --help`
Expected: Help message displayed

**Step 7: Commit**

Run:
```bash
git add src/firecrawl_cli/cli.py src/firecrawl_cli/commands/ tests/test_map.py
git commit -m "feat: add map command"
```

---

## Task 4: Scrape Command

**Files:**
- Create: `src/firecrawl_cli/commands/scrape.py`
- Create: `tests/test_scrape.py`

**Step 1: Write test for scrape command**

Create `tests/test_scrape.py`:
```python
from unittest.mock import Mock, patch, mock_open
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_scrape_to_stdout(monkeypatch):
    """Scrape command outputs markdown to stdout."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc = Mock()
    mock_doc.markdown = "# Test Content\n\nSome text."

    mock_client = Mock()
    mock_client.scrape.return_value = mock_doc

    with patch("firecrawl_cli.commands.scrape.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["scrape", "https://example.com"])

    assert result.exit_code == 0
    assert "# Test Content" in result.stdout
    mock_client.scrape.assert_called_once_with("https://example.com", formats=["markdown"])


def test_scrape_to_file(monkeypatch, tmp_path):
    """Scrape command saves to file with -o."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc = Mock()
    mock_doc.markdown = "# Test Content"

    mock_client = Mock()
    mock_client.scrape.return_value = mock_doc

    output_file = tmp_path / "output.md"

    with patch("firecrawl_cli.commands.scrape.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["scrape", "https://example.com", "-o", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.read_text() == "# Test Content"
    assert f"Saved to {output_file}" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scrape.py -v`
Expected: FAIL - scrape command not registered

**Step 3: Implement scrape command**

Create `src/firecrawl_cli/commands/scrape.py`:
```python
"""Scrape command implementation."""
import typer
from pathlib import Path
from typing import Optional
from firecrawl import Firecrawl
from firecrawl_cli.utils import get_api_key


def scrape_command(
    url: str = typer.Argument(..., help="URL to scrape"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
):
    """Scrape a single page to markdown."""
    try:
        api_key = get_api_key()
        firecrawl = Firecrawl(api_key=api_key)

        # Scrape URL
        doc = firecrawl.scrape(url, formats=["markdown"])

        markdown = doc.markdown

        if not markdown:
            typer.echo("No content scraped.", err=True)
            raise typer.Exit(1)

        # Output to file or stdout
        if output:
            output.write_text(markdown)
            typer.echo(f"Saved to {output}")
        else:
            typer.echo(markdown)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
```

**Step 4: Register scrape command in CLI**

Update `src/firecrawl_cli/cli.py`:
```python
"""Main CLI application."""
import typer
from typing import Optional


app = typer.Typer(
    name="firecrawl",
    help="CLI tool for Firecrawl API - map, scrape, crawl, and batch operations",
    no_args_is_help=True,
)


# Register commands
from firecrawl_cli.commands import map as map_cmd
from firecrawl_cli.commands import scrape as scrape_cmd

app.command(name="map")(map_cmd.map_command)
app.command(name="scrape")(scrape_cmd.scrape_command)


if __name__ == "__main__":
    app()
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_scrape.py -v`
Expected: PASS - all tests pass

**Step 6: Test CLI manually**

Run: `uv run firecrawl scrape --help`
Expected: Help message displayed

**Step 7: Commit**

Run:
```bash
git add src/firecrawl_cli/commands/scrape.py src/firecrawl_cli/cli.py tests/test_scrape.py
git commit -m "feat: add scrape command"
```

---

## Task 5: Crawl Command

**Files:**
- Create: `src/firecrawl_cli/commands/crawl.py`
- Create: `tests/test_crawl.py`

**Step 1: Write test for crawl command**

Create `tests/test_crawl.py`:
```python
from unittest.mock import Mock, patch
from pathlib import Path
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_crawl_to_stdout(monkeypatch):
    """Crawl command outputs all pages to stdout."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = {"sourceURL": "https://example.com/page1"}

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = {"sourceURL": "https://example.com/page2"}

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.crawl.return_value = mock_response

    with patch("firecrawl_cli.commands.crawl.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["crawl", "https://example.com"])

    assert result.exit_code == 0
    assert "# Page 1" in result.stdout
    assert "# Page 2" in result.stdout
    assert "https://example.com/page1" in result.stdout


def test_crawl_to_directory(monkeypatch, tmp_path):
    """Crawl command saves multiple files with -o."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = {"sourceURL": "https://example.com/page1"}

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = {"sourceURL": "https://example.com/page2"}

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.crawl.return_value = mock_response

    with patch("firecrawl_cli.commands.crawl.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["crawl", "https://example.com", "-o", str(tmp_path)])

    assert result.exit_code == 0

    # Check files created
    file1 = tmp_path / "example-com-page1.md"
    file2 = tmp_path / "example-com-page2.md"

    assert file1.exists()
    assert file2.exists()
    assert file1.read_text() == "# Page 1"
    assert file2.read_text() == "# Page 2"


def test_crawl_with_limit(monkeypatch):
    """Crawl respects limit parameter."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_response = Mock()
    mock_response.data = []

    mock_client = Mock()
    mock_client.crawl.return_value = mock_response

    with patch("firecrawl_cli.commands.crawl.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["crawl", "https://example.com", "--limit", "10"])

    mock_client.crawl.assert_called_once_with(
        url="https://example.com",
        limit=10,
        scrape_options={"formats": ["markdown"]}
    )
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_crawl.py -v`
Expected: FAIL - crawl command not registered

**Step 3: Implement crawl command**

Create `src/firecrawl_cli/commands/crawl.py`:
```python
"""Crawl command implementation."""
import typer
from pathlib import Path
from typing import Optional
from firecrawl import Firecrawl
from firecrawl_cli.utils import get_api_key, url_to_filename


def crawl_command(
    url: str = typer.Argument(..., help="URL to crawl"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Maximum number of pages to crawl"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output directory for files"),
):
    """Recursively crawl a website."""
    try:
        api_key = get_api_key()
        firecrawl = Firecrawl(api_key=api_key)

        typer.echo(f"Crawling {url}...")

        # Crawl URL
        response = firecrawl.crawl(
            url=url,
            limit=limit,
            scrape_options={"formats": ["markdown"]}
        )

        pages = response.data

        if not pages:
            typer.echo("No pages found.", err=True)
            raise typer.Exit(1)

        typer.echo(f"Found {len(pages)} pages\n")

        # Output to directory or stdout
        if output:
            output.mkdir(parents=True, exist_ok=True)

            for doc in pages:
                source_url = doc.metadata.get("sourceURL", "")
                filename = url_to_filename(source_url)
                filepath = output / filename

                filepath.write_text(doc.markdown)
                typer.echo(f"Saved {source_url} -> {filepath}")

            typer.echo(f"\nSaved {len(pages)} pages to {output}")
        else:
            # Output to stdout with separators
            for i, doc in enumerate(pages):
                source_url = doc.metadata.get("sourceURL", "")

                typer.echo(f"{'='*60}")
                typer.echo(f"Page {i+1}/{len(pages)}: {source_url}")
                typer.echo(f"{'='*60}\n")
                typer.echo(doc.markdown)
                typer.echo("\n")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
```

**Step 4: Register crawl command**

Update `src/firecrawl_cli/cli.py`:
```python
"""Main CLI application."""
import typer
from typing import Optional


app = typer.Typer(
    name="firecrawl",
    help="CLI tool for Firecrawl API - map, scrape, crawl, and batch operations",
    no_args_is_help=True,
)


# Register commands
from firecrawl_cli.commands import map as map_cmd
from firecrawl_cli.commands import scrape as scrape_cmd
from firecrawl_cli.commands import crawl as crawl_cmd

app.command(name="map")(map_cmd.map_command)
app.command(name="scrape")(scrape_cmd.scrape_command)
app.command(name="crawl")(crawl_cmd.crawl_command)


if __name__ == "__main__":
    app()
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_crawl.py -v`
Expected: PASS - all tests pass

**Step 6: Test CLI manually**

Run: `uv run firecrawl crawl --help`
Expected: Help message displayed

**Step 7: Commit**

Run:
```bash
git add src/firecrawl_cli/commands/crawl.py src/firecrawl_cli/cli.py tests/test_crawl.py
git commit -m "feat: add crawl command"
```

---

## Task 6: Batch Command

**Files:**
- Create: `src/firecrawl_cli/commands/batch.py`
- Create: `tests/test_batch.py`

**Step 1: Write test for batch command**

Create `tests/test_batch.py`:
```python
from unittest.mock import Mock, patch
from pathlib import Path
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_batch_from_args(monkeypatch, tmp_path):
    """Batch scrape from command line URLs."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = {"sourceURL": "https://example.com/page1"}

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = {"sourceURL": "https://example.com/page2"}

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.batch_scrape.return_value = mock_response

    with patch("firecrawl_cli.commands.batch.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, [
            "batch",
            "https://example.com/page1",
            "https://example.com/page2",
            "-o", str(tmp_path)
        ])

    assert result.exit_code == 0

    file1 = tmp_path / "example-com-page1.md"
    file2 = tmp_path / "example-com-page2.md"

    assert file1.exists()
    assert file2.exists()


def test_batch_from_file(monkeypatch, tmp_path):
    """Batch scrape from URL file."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    # Create URL file
    url_file = tmp_path / "urls.txt"
    url_file.write_text("https://example.com/page1\nhttps://example.com/page2")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = {"sourceURL": "https://example.com/page1"}

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = {"sourceURL": "https://example.com/page2"}

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.batch_scrape.return_value = mock_response

    output_dir = tmp_path / "output"

    with patch("firecrawl_cli.commands.batch.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, [
            "batch",
            "--source", str(url_file),
            "-o", str(output_dir)
        ])

    assert result.exit_code == 0

    file1 = output_dir / "example-com-page1.md"
    file2 = output_dir / "example-com-page2.md"

    assert file1.exists()
    assert file2.exists()


def test_batch_requires_output(monkeypatch):
    """Batch command requires -o flag."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    result = runner.invoke(app, ["batch", "https://example.com/page1"])

    assert result.exit_code != 0
    assert "required" in result.stdout.lower() or "missing" in result.stdout.lower()


def test_batch_requires_urls_or_source(monkeypatch, tmp_path):
    """Batch command requires either URLs or --source."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    result = runner.invoke(app, ["batch", "-o", str(tmp_path)])

    assert result.exit_code != 0
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_batch.py -v`
Expected: FAIL - batch command not registered

**Step 3: Implement batch command**

Create `src/firecrawl_cli/commands/batch.py`:
```python
"""Batch command implementation."""
import typer
from pathlib import Path
from typing import List, Optional
from firecrawl import Firecrawl
from firecrawl_cli.utils import get_api_key, url_to_filename


def batch_command(
    urls: List[str] = typer.Argument(None, help="URLs to scrape"),
    source: Optional[Path] = typer.Option(None, "--source", help="File containing URLs (one per line)"),
    output: Path = typer.Option(..., "-o", "--output", help="Output directory (required)"),
):
    """Batch scrape multiple URLs."""
    try:
        # Validate inputs
        url_list = []

        if source:
            # Read URLs from file
            if not source.exists():
                typer.echo(f"Error: File not found: {source}", err=True)
                raise typer.Exit(1)

            url_list = [
                line.strip()
                for line in source.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]
        elif urls:
            url_list = urls
        else:
            typer.echo("Error: Provide URLs as arguments or use --source <file>", err=True)
            raise typer.Exit(1)

        if not url_list:
            typer.echo("Error: No URLs to scrape", err=True)
            raise typer.Exit(1)

        typer.echo(f"Batch scraping {len(url_list)} URLs...")

        api_key = get_api_key()
        firecrawl = Firecrawl(api_key=api_key)

        # Batch scrape
        response = firecrawl.batch_scrape(url_list, formats=["markdown"])

        pages = response.data

        if not pages:
            typer.echo("No pages scraped.", err=True)
            raise typer.Exit(1)

        # Create output directory
        output.mkdir(parents=True, exist_ok=True)

        # Save each page
        for doc in pages:
            source_url = doc.metadata.get("sourceURL", "")
            filename = url_to_filename(source_url)
            filepath = output / filename

            filepath.write_text(doc.markdown)
            typer.echo(f"Saved {source_url} -> {filepath}")

        typer.echo(f"\nSaved {len(pages)} pages to {output}")

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
```

**Step 4: Register batch command**

Update `src/firecrawl_cli/cli.py`:
```python
"""Main CLI application."""
import typer
from typing import Optional


app = typer.Typer(
    name="firecrawl",
    help="CLI tool for Firecrawl API - map, scrape, crawl, and batch operations",
    no_args_is_help=True,
)


# Register commands
from firecrawl_cli.commands import map as map_cmd
from firecrawl_cli.commands import scrape as scrape_cmd
from firecrawl_cli.commands import crawl as crawl_cmd
from firecrawl_cli.commands import batch as batch_cmd

app.command(name="map")(map_cmd.map_command)
app.command(name="scrape")(scrape_cmd.scrape_command)
app.command(name="crawl")(crawl_cmd.crawl_command)
app.command(name="batch")(batch_cmd.batch_command)


if __name__ == "__main__":
    app()
```

**Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_batch.py -v`
Expected: PASS - all tests pass

**Step 6: Test CLI manually**

Run: `uv run firecrawl batch --help`
Expected: Help message displayed

**Step 7: Commit**

Run:
```bash
git add src/firecrawl_cli/commands/batch.py src/firecrawl_cli/cli.py tests/test_batch.py
git commit -m "feat: add batch command"
```

---

## Task 7: README and Installation

**Files:**
- Create: `README.md`

**Step 1: Write README**

Create `README.md`:
```markdown
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
```

**Step 2: Test installation**

Run:
```bash
uv tool install .
firecrawl --help
```

Expected: Help message displayed, tool installed globally

**Step 3: Commit**

Run:
```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

## Task 8: Final Integration Test

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write integration test**

Create `tests/test_integration.py`:
```python
"""Integration tests for the CLI."""
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_cli_help():
    """CLI shows help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "firecrawl" in result.stdout.lower()


def test_all_commands_registered():
    """All commands are registered."""
    result = runner.invoke(app, ["--help"])
    assert "map" in result.stdout
    assert "scrape" in result.stdout
    assert "crawl" in result.stdout
    assert "batch" in result.stdout


def test_map_help():
    """Map command has help."""
    result = runner.invoke(app, ["map", "--help"])
    assert result.exit_code == 0
    assert "URL" in result.stdout


def test_scrape_help():
    """Scrape command has help."""
    result = runner.invoke(app, ["scrape", "--help"])
    assert result.exit_code == 0
    assert "URL" in result.stdout


def test_crawl_help():
    """Crawl command has help."""
    result = runner.invoke(app, ["crawl", "--help"])
    assert result.exit_code == 0
    assert "URL" in result.stdout


def test_batch_help():
    """Batch command has help."""
    result = runner.invoke(app, ["batch", "--help"])
    assert result.exit_code == 0
    assert "URL" in result.stdout or "output" in result.stdout
```

**Step 2: Run all tests**

Run: `uv run pytest -v`
Expected: All tests pass

**Step 3: Run test coverage**

Run: `uv run pytest --cov=src/firecrawl_cli --cov-report=term-missing`
Expected: High coverage (>80%)

**Step 4: Final commit**

Run:
```bash
git add tests/test_integration.py
git commit -m "test: add integration tests"
```

---

## Completion Checklist

- [ ] All commands implemented (map, scrape, crawl, batch)
- [ ] All tests passing
- [ ] README with usage examples
- [ ] Tool installable via `uv tool install`
- [ ] API key validation working
- [ ] URL to filename conversion working
- [ ] Output to stdout and files working
- [ ] Error handling for API failures

## Next Steps

After implementation:
1. Test with real Firecrawl API key
2. Add `.gitignore` for Python projects
3. Consider adding progress bars for long operations
4. Consider adding `--json` output format for scripting

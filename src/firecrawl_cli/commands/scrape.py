"""Scrape command implementation."""
import typer
from pathlib import Path
from typing import Optional
from firecrawl import Firecrawl
from firecrawl_cli.utils import get_api_key


def scrape_command(
    url: str = typer.Argument(..., help="URL to scrape"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
    refresh: bool = typer.Option(False, "--refresh", help="Force fresh scrape (skip cache)"),
):
    """Scrape a single page to markdown (fast by default, uses cache)."""
    try:
        api_key = get_api_key()
        firecrawl = Firecrawl(api_key=api_key)

        # Scrape URL with max_age parameter
        # Default: uses cache (fast, up to 500% faster)
        # --refresh: forces fresh scrape (max_age=0)
        if refresh:
            doc = firecrawl.scrape(url, formats=["markdown"], max_age=0)
        else:
            # Don't pass max_age to use API default (2 days cache)
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

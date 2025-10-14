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
                source_url = doc.metadata.source_url if doc.metadata else ""
                filename = url_to_filename(source_url)
                filepath = output / filename

                filepath.write_text(doc.markdown)
                typer.echo(f"Saved {source_url} -> {filepath}")

            typer.echo(f"\nSaved {len(pages)} pages to {output}")
        else:
            # Output to stdout with separators
            for i, doc in enumerate(pages):
                source_url = doc.metadata.source_url if doc.metadata else ""

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

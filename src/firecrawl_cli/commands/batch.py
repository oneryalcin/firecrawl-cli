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
            source_url = doc.metadata.source_url or ""
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

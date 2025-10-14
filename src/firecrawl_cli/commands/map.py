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
        links = result.links if hasattr(result, 'links') else []

        if not links:
            typer.echo("No links found.")
            return

        typer.echo(f"Found {len(links)} links:\n")

        for link in links:
            link_url = link.url if hasattr(link, 'url') else link.get("url", "")
            title = link.title if hasattr(link, 'title') else link.get("title", "")

            if title:
                typer.echo(f"{link_url} - {title}")
            else:
                typer.echo(link_url)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

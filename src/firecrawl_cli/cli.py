"""Main CLI application."""
import typer
from typing import Optional

__version__ = "0.1.0"


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"firecrawl version {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="firecrawl",
    help="CLI tool for Firecrawl API - map, scrape, crawl, and batch operations",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    )
):
    """CLI tool for Firecrawl API."""
    pass


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

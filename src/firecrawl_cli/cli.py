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

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

from unittest.mock import Mock, patch
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_map_basic(monkeypatch):
    """Map command outputs URLs to stdout."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    # Create mock link objects
    mock_link1 = Mock()
    mock_link1.url = "https://example.com/page1"
    mock_link1.title = "Page 1"

    mock_link2 = Mock()
    mock_link2.url = "https://example.com/page2"
    mock_link2.title = "Page 2"

    # Create mock result with links attribute
    mock_result = Mock()
    mock_result.links = [mock_link1, mock_link2]

    mock_client = Mock()
    mock_client.map.return_value = mock_result

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        # Note: When only one command exists, Typer doesn't use subcommand syntax
        result = runner.invoke(app, ["https://example.com"])

    assert result.exit_code == 0
    assert "https://example.com/page1" in result.stdout
    assert "https://example.com/page2" in result.stdout
    assert "Page 1" in result.stdout


def test_map_with_limit(monkeypatch):
    """Map command respects limit parameter."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_result = Mock()
    mock_result.links = []

    mock_client = Mock()
    mock_client.map.return_value = mock_result

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        # Note: When only one command exists, Typer doesn't use subcommand syntax
        result = runner.invoke(app, ["https://example.com", "--limit", "50"])

    mock_client.map.assert_called_once_with(
        url="https://example.com",
        limit=50,
        search=None
    )
    assert result.exit_code == 0


def test_map_with_search(monkeypatch):
    """Map command supports search parameter."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_result = Mock()
    mock_result.links = []

    mock_client = Mock()
    mock_client.map.return_value = mock_result

    with patch("firecrawl_cli.commands.map.Firecrawl", return_value=mock_client):
        # Note: When only one command exists, Typer doesn't use subcommand syntax
        result = runner.invoke(app, ["https://example.com", "--search", "docs"])

    mock_client.map.assert_called_once_with(
        url="https://example.com",
        limit=None,
        search="docs"
    )
    assert result.exit_code == 0

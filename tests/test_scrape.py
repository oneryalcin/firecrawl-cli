from unittest.mock import Mock, patch, mock_open
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_scrape_to_stdout(monkeypatch):
    """Scrape command outputs markdown to stdout (uses cache by default)."""
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


def test_scrape_with_refresh(monkeypatch):
    """Scrape command forces fresh scrape with --refresh flag."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc = Mock()
    mock_doc.markdown = "# Fresh Content"

    mock_client = Mock()
    mock_client.scrape.return_value = mock_doc

    with patch("firecrawl_cli.commands.scrape.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, ["scrape", "https://example.com", "--refresh"])

    assert result.exit_code == 0
    assert "# Fresh Content" in result.stdout
    # --refresh should set max_age=0 to force fresh scrape
    mock_client.scrape.assert_called_once_with("https://example.com", formats=["markdown"], max_age=0)

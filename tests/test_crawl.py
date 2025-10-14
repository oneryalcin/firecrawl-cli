from unittest.mock import Mock, patch
from pathlib import Path
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_crawl_to_stdout(monkeypatch):
    """Crawl command outputs all pages to stdout."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_metadata1 = Mock()
    mock_metadata1.source_url = "https://example.com/page1"

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = mock_metadata1

    mock_metadata2 = Mock()
    mock_metadata2.source_url = "https://example.com/page2"

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = mock_metadata2

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

    mock_metadata1 = Mock()
    mock_metadata1.source_url = "https://example.com/page1"

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = mock_metadata1

    mock_metadata2 = Mock()
    mock_metadata2.source_url = "https://example.com/page2"

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = mock_metadata2

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

    mock_metadata1 = Mock()
    mock_metadata1.source_url = "https://example.com/test"

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Test"
    mock_doc1.metadata = mock_metadata1

    mock_response = Mock()
    mock_response.data = [mock_doc1]

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

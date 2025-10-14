from unittest.mock import Mock, patch
from pathlib import Path
from typer.testing import CliRunner
from firecrawl_cli.cli import app


runner = CliRunner()


def test_batch_from_args(monkeypatch, tmp_path):
    """Batch scrape from command line URLs."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = Mock(source_url="https://example.com/page1")

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = Mock(source_url="https://example.com/page2")

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.batch_scrape.return_value = mock_response

    with patch("firecrawl_cli.commands.batch.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, [
            "batch",
            "https://example.com/page1",
            "https://example.com/page2",
            "-o", str(tmp_path)
        ])

    assert result.exit_code == 0

    file1 = tmp_path / "example-com-page1.md"
    file2 = tmp_path / "example-com-page2.md"

    assert file1.exists()
    assert file2.exists()


def test_batch_from_file(monkeypatch, tmp_path):
    """Batch scrape from URL file."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    # Create URL file
    url_file = tmp_path / "urls.txt"
    url_file.write_text("https://example.com/page1\nhttps://example.com/page2")

    mock_doc1 = Mock()
    mock_doc1.markdown = "# Page 1"
    mock_doc1.metadata = Mock(source_url="https://example.com/page1")

    mock_doc2 = Mock()
    mock_doc2.markdown = "# Page 2"
    mock_doc2.metadata = Mock(source_url="https://example.com/page2")

    mock_response = Mock()
    mock_response.data = [mock_doc1, mock_doc2]

    mock_client = Mock()
    mock_client.batch_scrape.return_value = mock_response

    output_dir = tmp_path / "output"

    with patch("firecrawl_cli.commands.batch.Firecrawl", return_value=mock_client):
        result = runner.invoke(app, [
            "batch",
            "--source", str(url_file),
            "-o", str(output_dir)
        ])

    assert result.exit_code == 0

    file1 = output_dir / "example-com-page1.md"
    file2 = output_dir / "example-com-page2.md"

    assert file1.exists()
    assert file2.exists()


def test_batch_requires_output(monkeypatch):
    """Batch command requires -o flag."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    result = runner.invoke(app, ["batch", "https://example.com/page1"])

    assert result.exit_code != 0
    assert "missing" in result.output.lower()


def test_batch_requires_urls_or_source(monkeypatch, tmp_path):
    """Batch command requires either URLs or --source."""
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")

    result = runner.invoke(app, ["batch", "-o", str(tmp_path)])

    assert result.exit_code != 0

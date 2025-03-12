"""
Tests for the news collector module.
"""
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from bs4 import BeautifulSoup

from src.news_summarizer.data_collection.collector import NewsCollector


class TestNewsCollector(unittest.TestCase):
    """Test cases for the NewsCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_sources = [
            {"name": "Test Source 1", "url": "https://example.com/news1"},
            {"name": "Test Source 2", "url": "https://example.com/news2"},
        ]
        self.collector = NewsCollector(
            sources=self.test_sources,
            max_articles_per_source=2,
            days_to_look_back=1,
        )

    @patch("src.news_summarizer.data_collection.collector.requests.get")
    def test_collect_from_source(self, mock_get):
        """Test collecting articles from a source."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = """
        <html>
            <body>
                <a href="https://example.com/article1">Article 1</a>
                <a href="https://example.com/article2">Article 2</a>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Mock the extract_article_content method
        self.collector._extract_article_content = MagicMock(
            side_effect=[
                {
                    "title": "Test Article 1",
                    "text": "This is test article 1",
                    "url": "https://example.com/article1",
                    "source": "Test Source 1",
                    "date": pd.Timestamp.now(),
                },
                {
                    "title": "Test Article 2",
                    "text": "This is test article 2",
                    "url": "https://example.com/article2",
                    "source": "Test Source 1",
                    "date": pd.Timestamp.now(),
                },
            ]
        )
        
        # Call the method
        articles = self.collector._collect_from_source(self.test_sources[0])
        
        # Assertions
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Test Article 1")
        self.assertEqual(articles[1]["title"], "Test Article 2")
        
        # Verify the mocks were called correctly
        mock_get.assert_called_once_with(
            self.test_sources[0]["url"],
            headers=self.collector.headers,
            timeout=10,
        )
        self.assertEqual(self.collector._extract_article_content.call_count, 2)

    def test_extract_article_links(self):
        """Test extracting article links from HTML."""
        # Create a test HTML
        html = """
        <html>
            <body>
                <a href="https://example.com/article1">Article 1</a>
                <a href="/article2">Article 2</a>
                <a href="article3">Article 3</a>
                <a href="#">Not an article</a>
                <a href="javascript:void(0)">Also not an article</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        base_url = "https://example.com"
        
        # Call the method
        links = self.collector._extract_article_links(soup, base_url)
        
        # Assertions
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0], "https://example.com/article1")
        self.assertEqual(links[1], "https://example.com/article2")
        self.assertEqual(links[2], "https://example.com/article3")


if __name__ == "__main__":
    unittest.main() 
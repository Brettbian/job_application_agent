"""
Tests for the formatter module.
"""
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from src.news_summarizer.utils.formatter import NewsletterFormatter


class TestNewsletterFormatter(unittest.TestCase):
    """Test cases for the NewsletterFormatter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_articles = [
            {
                "title": "Test Article 1",
                "humorous_content": "This is a humorous summary of article 1.",
                "url": "https://example.com/article1",
                "source": "Test Source 1",
            },
            {
                "title": "Test Article 2",
                "humorous_content": "This is a humorous summary of article 2.",
                "url": "https://example.com/article2",
                "source": "Test Source 2",
            },
        ]
        
        # Create a temporary directory for output
        self.temp_dir = tempfile.mkdtemp()
        
        # Create formatters for testing
        self.md_formatter = NewsletterFormatter(
            output_format="markdown",
            output_directory=self.temp_dir,
        )
        self.html_formatter = NewsletterFormatter(
            output_format="html",
            output_directory=self.temp_dir,
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))
        
        # Remove temporary directory
        os.rmdir(self.temp_dir)

    def test_format_markdown(self):
        """Test formatting articles as markdown."""
        # Call the method
        markdown = self.md_formatter._format_markdown(self.test_articles)
        
        # Assertions
        self.assertIn("# AI News with a Twist", markdown)
        self.assertIn("## Test Article 1", markdown)
        self.assertIn("This is a humorous summary of article 1.", markdown)
        self.assertIn("*Source: [Test Source 1](https://example.com/article1)*", markdown)
        self.assertIn("## Test Article 2", markdown)
        self.assertIn("This is a humorous summary of article 2.", markdown)
        self.assertIn("*Source: [Test Source 2](https://example.com/article2)*", markdown)
        self.assertIn("*Generated on", markdown)

    def test_format_html(self):
        """Test formatting articles as HTML."""
        # Call the method
        html = self.html_formatter._format_html(self.test_articles)
        
        # Assertions
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>AI News with a Twist", html)
        self.assertIn("<h2>Test Article 1</h2>", html)
        self.assertIn("This is a humorous summary of article 1.", html)
        self.assertIn('<a href="https://example.com/article1" target="_blank">Test Source 1</a>', html)
        self.assertIn("<h2>Test Article 2</h2>", html)
        self.assertIn("This is a humorous summary of article 2.", html)
        self.assertIn('<a href="https://example.com/article2" target="_blank">Test Source 2</a>', html)
        self.assertIn("Generated on", html)

    @patch("src.news_summarizer.utils.formatter.datetime")
    def test_save_newsletter_markdown(self, mock_datetime):
        """Test saving a markdown newsletter."""
        # Mock the datetime to get a consistent filename
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Create content to save
        content = "# Test Newsletter"
        
        # Call the method
        filepath = self.md_formatter.save_newsletter(content)
        
        # Assertions
        expected_path = os.path.join(self.temp_dir, "ai_news_2023-01-01.md")
        self.assertEqual(filepath, expected_path)
        self.assertTrue(os.path.exists(filepath))
        
        # Check the content
        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, content)

    @patch("src.news_summarizer.utils.formatter.datetime")
    def test_save_newsletter_html(self, mock_datetime):
        """Test saving an HTML newsletter."""
        # Mock the datetime to get a consistent filename
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Create content to save
        content = "<html><body>Test Newsletter</body></html>"
        
        # Call the method
        filepath = self.html_formatter.save_newsletter(content)
        
        # Assertions
        expected_path = os.path.join(self.temp_dir, "ai_news_2023-01-01.html")
        self.assertEqual(filepath, expected_path)
        self.assertTrue(os.path.exists(filepath))
        
        # Check the content
        with open(filepath, "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertEqual(saved_content, content)


if __name__ == "__main__":
    unittest.main() 
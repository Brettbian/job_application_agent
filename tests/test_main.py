"""
Tests for the main module.
"""
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.news_summarizer.main import (
    add_humor,
    collect_news,
    format_and_save,
    main,
    summarize_articles,
)


class TestMainModule(unittest.TestCase):
    """Test cases for the main module functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = lambda key, default=None: {
            "max_articles_per_source": 5,
            "days_to_look_back": 3,
            "summarization_model": "test/model",
            "summary_min_length": 50,
            "summary_max_length": 150,
            "humor_model": "test-model",
            "humor_temperature": 0.7,
            "output_format": "markdown",
            "output_directory": "./output",
        }.get(key, default)
        
        # Create a test DataFrame
        self.test_df = pd.DataFrame(
            [
                {
                    "title": "Test Article 1",
                    "text": "This is the text of test article 1.",
                    "url": "https://example.com/article1",
                    "source": "Test Source 1",
                    "date": pd.Timestamp.now(),
                },
                {
                    "title": "Test Article 2",
                    "text": "This is the text of test article 2.",
                    "url": "https://example.com/article2",
                    "source": "Test Source 2",
                    "date": pd.Timestamp.now(),
                },
            ]
        )

    @patch("src.news_summarizer.main.NewsCollector")
    def test_collect_news(self, mock_collector_class):
        """Test collecting news."""
        # Set up mock
        mock_collector_instance = MagicMock()
        mock_collector_instance.collect_news.return_value = self.test_df
        mock_collector_class.return_value = mock_collector_instance
        
        # Call the function
        result_df = collect_news(self.mock_config)
        
        # Assertions
        self.assertEqual(len(result_df), 2)
        mock_collector_class.assert_called_once_with(
            max_articles_per_source=5,
            days_to_look_back=3,
        )
        mock_collector_instance.collect_news.assert_called_once()

    @patch("src.news_summarizer.main.ArticleSummarizer")
    def test_summarize_articles(self, mock_summarizer_class):
        """Test summarizing articles."""
        # Set up mock
        mock_summarizer_instance = MagicMock()
        mock_summarizer_instance.summarize.side_effect = lambda text: f"Summary of: {text}"
        mock_summarizer_class.return_value = mock_summarizer_instance
        
        # Call the function
        result_df = summarize_articles(self.test_df.copy(), self.mock_config)
        
        # Assertions
        self.assertEqual(len(result_df), 2)
        self.assertTrue("summary" in result_df.columns)
        self.assertEqual(
            result_df["summary"].iloc[0], "Summary of: This is the text of test article 1."
        )
        self.assertEqual(
            result_df["summary"].iloc[1], "Summary of: This is the text of test article 2."
        )
        mock_summarizer_class.assert_called_once_with(
            model_name="test/model",
            min_length=50,
            max_length=150,
        )

    @patch("src.news_summarizer.main.HumorGenerator")
    def test_add_humor(self, mock_humorizer_class):
        """Test adding humor to summaries."""
        # Add summary column to test DataFrame
        test_df = self.test_df.copy()
        test_df["summary"] = [
            "Summary of article 1.",
            "Summary of article 2.",
        ]
        
        # Set up mock
        mock_humorizer_instance = MagicMock()
        mock_humorizer_instance.add_humor.side_effect = lambda title, summary: f"Humorous version of: {title} - {summary}"
        mock_humorizer_class.return_value = mock_humorizer_instance
        
        # Call the function
        result_df = add_humor(test_df, self.mock_config)
        
        # Assertions
        self.assertEqual(len(result_df), 2)
        self.assertTrue("humorous_content" in result_df.columns)
        self.assertEqual(
            result_df["humorous_content"].iloc[0],
            "Humorous version of: Test Article 1 - Summary of article 1.",
        )
        self.assertEqual(
            result_df["humorous_content"].iloc[1],
            "Humorous version of: Test Article 2 - Summary of article 2.",
        )
        mock_humorizer_class.assert_called_once_with(
            model="test-model",
            temperature=0.7,
        )

    @patch("src.news_summarizer.main.NewsletterFormatter")
    def test_format_and_save(self, mock_formatter_class):
        """Test formatting and saving the newsletter."""
        # Add required columns to test DataFrame
        test_df = self.test_df.copy()
        test_df["summary"] = [
            "Summary of article 1.",
            "Summary of article 2.",
        ]
        test_df["humorous_content"] = [
            "Humorous version of article 1.",
            "Humorous version of article 2.",
        ]
        
        # Set up mock
        mock_formatter_instance = MagicMock()
        mock_formatter_instance.format_newsletter.return_value = "Formatted newsletter content"
        mock_formatter_instance.save_newsletter.return_value = "/path/to/saved/newsletter.md"
        mock_formatter_class.return_value = mock_formatter_instance
        
        # Call the function
        result_path = format_and_save(test_df, self.mock_config)
        
        # Assertions
        self.assertEqual(result_path, "/path/to/saved/newsletter.md")
        mock_formatter_class.assert_called_once_with(
            output_format="markdown",
            output_directory="./output",
        )
        mock_formatter_instance.format_newsletter.assert_called_once()
        mock_formatter_instance.save_newsletter.assert_called_once_with(
            "Formatted newsletter content"
        )

    @patch("src.news_summarizer.main.load_config")
    @patch("src.news_summarizer.main.collect_news")
    @patch("src.news_summarizer.main.summarize_articles")
    @patch("src.news_summarizer.main.add_humor")
    @patch("src.news_summarizer.main.format_and_save")
    def test_main_success(
        self,
        mock_format_and_save,
        mock_add_humor,
        mock_summarize_articles,
        mock_collect_news,
        mock_load_config,
    ):
        """Test the main function with successful execution."""
        # Set up mocks
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        
        mock_collect_news.return_value = self.test_df
        mock_summarize_articles.return_value = self.test_df
        mock_add_humor.return_value = self.test_df
        mock_format_and_save.return_value = "/path/to/saved/newsletter.md"
        
        # Call the function
        result = main()
        
        # Assertions
        self.assertEqual(result, 0)  # Should return 0 for success
        mock_load_config.assert_called_once()
        mock_collect_news.assert_called_once_with(mock_config)
        mock_summarize_articles.assert_called_once_with(self.test_df, mock_config)
        mock_add_humor.assert_called_once_with(self.test_df, mock_config)
        mock_format_and_save.assert_called_once_with(self.test_df, mock_config)

    @patch("src.news_summarizer.main.load_config")
    @patch("src.news_summarizer.main.collect_news")
    def test_main_no_articles(self, mock_collect_news, mock_load_config):
        """Test the main function when no articles are collected."""
        # Set up mocks
        mock_config = MagicMock()
        mock_load_config.return_value = mock_config
        
        # Return an empty DataFrame
        mock_collect_news.return_value = pd.DataFrame()
        
        # Call the function
        result = main()
        
        # Assertions
        self.assertEqual(result, 1)  # Should return 1 for failure
        mock_load_config.assert_called_once()
        mock_collect_news.assert_called_once_with(mock_config)


if __name__ == "__main__":
    unittest.main() 
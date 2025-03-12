"""
Tests for the configuration module.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

from src.news_summarizer.utils.config import Config, load_config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary .env file for testing
        self.temp_env = tempfile.NamedTemporaryFile(delete=False, mode="w")
        self.temp_env.write(
            """
            OPENAI_API_KEY=test_api_key
            MAX_ARTICLES_PER_SOURCE=10
            DAYS_TO_LOOK_BACK=5
            SUMMARY_MIN_LENGTH=30
            SUMMARY_MAX_LENGTH=100
            SUMMARIZATION_MODEL=test/model
            HUMOR_TEMPERATURE=0.5
            HUMOR_MODEL=test-model
            OUTPUT_FORMAT=html
            OUTPUT_DIRECTORY=./test_output
            """
        )
        self.temp_env.close()

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        os.unlink(self.temp_env.name)

    def test_load_config(self):
        """Test loading configuration from a file."""
        # Load configuration from the temporary file
        config = Config(env_file=self.temp_env.name)
        
        # Assertions
        self.assertEqual(config.config["openai_api_key"], "test_api_key")
        self.assertEqual(config.config["max_articles_per_source"], 10)
        self.assertEqual(config.config["days_to_look_back"], 5)
        self.assertEqual(config.config["summary_min_length"], 30)
        self.assertEqual(config.config["summary_max_length"], 100)
        self.assertEqual(config.config["summarization_model"], "test/model")
        self.assertEqual(config.config["humor_temperature"], 0.5)
        self.assertEqual(config.config["humor_model"], "test-model")
        self.assertEqual(config.config["output_format"], "html")
        self.assertEqual(config.config["output_directory"], "./test_output")

    def test_get_method(self):
        """Test the get method."""
        # Load configuration from the temporary file
        config = Config(env_file=self.temp_env.name)
        
        # Assertions
        self.assertEqual(config.get("openai_api_key"), "test_api_key")
        self.assertEqual(config.get("nonexistent_key", "default"), "default")

    @patch.dict(os.environ, {"HUMOR_TEMPERATURE": "2.0"})
    def test_validate_temperature(self):
        """Test validation of temperature value."""
        # Load configuration with an invalid temperature
        config = Config()
        
        # Assertions
        self.assertEqual(config.config["humor_temperature"], 0.7)  # Should be reset to default

    @patch.dict(os.environ, {"OUTPUT_FORMAT": "invalid"})
    def test_validate_output_format(self):
        """Test validation of output format."""
        # Load configuration with an invalid output format
        config = Config()
        
        # Assertions
        self.assertEqual(config.config["output_format"], "markdown")  # Should be reset to default

    @patch.dict(os.environ, {"MAX_ARTICLES_PER_SOURCE": "-1"})
    def test_validate_numeric_values(self):
        """Test validation of numeric values."""
        # Load configuration with invalid numeric values
        config = Config()
        
        # Assertions
        self.assertEqual(config.config["max_articles_per_source"], 5)  # Should be reset to default


if __name__ == "__main__":
    unittest.main() 
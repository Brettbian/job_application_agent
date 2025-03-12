"""
Configuration module for loading and validating environment variables.
"""
import logging
import os
from typing import Dict, Optional

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Config:
    """Class for loading and validating configuration from environment variables."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the Config.

        Args:
            env_file: Path to the .env file
        """
        # Load environment variables
        load_dotenv(dotenv_path=env_file)
        
        # Load configuration
        self.config = self._load_config()
        
        # Validate configuration
        self._validate_config()

    def _load_config(self) -> Dict:
        """
        Load configuration from environment variables.

        Returns:
            Dictionary with configuration values
        """
        return {
            # API Keys
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            
            # News Collection Settings
            "max_articles_per_source": int(os.getenv("MAX_ARTICLES_PER_SOURCE", "5")),
            "days_to_look_back": int(os.getenv("DAYS_TO_LOOK_BACK", "3")),
            
            # Summarization Settings
            "summary_min_length": int(os.getenv("SUMMARY_MIN_LENGTH", "50")),
            "summary_max_length": int(os.getenv("SUMMARY_MAX_LENGTH", "150")),
            "summarization_model": os.getenv(
                "SUMMARIZATION_MODEL", "google/pegasus-cnn_dailymail"
            ),
            
            # Humor Settings
            "humor_temperature": float(os.getenv("HUMOR_TEMPERATURE", "0.7")),
            "humor_model": os.getenv("HUMOR_MODEL", "gpt-4"),
            
            # Output Settings
            "output_format": os.getenv("OUTPUT_FORMAT", "markdown"),
            "output_directory": os.getenv("OUTPUT_DIRECTORY", "./output"),
        }

    def _validate_config(self):
        """Validate the configuration and log warnings for missing values."""
        # Check for required API keys
        if not self.config["openai_api_key"]:
            logger.warning(
                "OpenAI API key not found. Humor generation will not work. "
                "Please set the OPENAI_API_KEY environment variable."
            )
        
        # Validate numeric values
        for key in [
            "max_articles_per_source",
            "days_to_look_back",
            "summary_min_length",
            "summary_max_length",
        ]:
            if self.config[key] <= 0:
                logger.warning(
                    f"Invalid value for {key}: {self.config[key]}. "
                    f"Using default value instead."
                )
                # Set default values
                if key == "max_articles_per_source":
                    self.config[key] = 5
                elif key == "days_to_look_back":
                    self.config[key] = 3
                elif key == "summary_min_length":
                    self.config[key] = 50
                elif key == "summary_max_length":
                    self.config[key] = 150
        
        # Validate temperature
        if not (0.0 <= self.config["humor_temperature"] <= 1.0):
            logger.warning(
                f"Invalid value for humor_temperature: {self.config['humor_temperature']}. "
                f"Using default value 0.7 instead."
            )
            self.config["humor_temperature"] = 0.7
        
        # Validate output format
        if self.config["output_format"] not in ["markdown", "html"]:
            logger.warning(
                f"Invalid value for output_format: {self.config['output_format']}. "
                f"Using default value 'markdown' instead."
            )
            self.config["output_format"] = "markdown"

    def get(self, key: str, default: Optional[str] = None) -> any:
        """
        Get a configuration value.

        Args:
            key: The configuration key
            default: Default value if the key is not found

        Returns:
            The configuration value
        """
        return self.config.get(key, default)


def load_config(env_file: Optional[str] = None) -> Config:
    """
    Load configuration from environment variables.

    Args:
        env_file: Path to the .env file

    Returns:
        Config object
    """
    return Config(env_file=env_file)


def main():
    """Run the config module as a standalone module."""
    # Load configuration
    config = load_config()
    
    # Print configuration
    print("Configuration:")
    for key, value in config.config.items():
        # Mask API keys
        if "api_key" in key and value:
            masked_value = value[:4] + "..." + value[-4:]
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main() 
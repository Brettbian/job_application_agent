"""
Humor generation module for adding wit and humor to news summaries.
"""
import logging
import os
from typing import Dict, List, Optional, Union

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HumorGenerator:
    """Class for adding humor to news summaries using OpenAI's API."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        """
        Initialize the HumorGenerator.

        Args:
            model: The OpenAI model to use
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum number of tokens to generate
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Check if API key is available
        if not openai.api_key:
            logger.warning("OpenAI API key not found. Humor generation will not work.")

    def add_humor(self, title: str, summary: str) -> str:
        """
        Add humor to a news summary.

        Args:
            title: The title of the article
            summary: The summary of the article

        Returns:
            A humorous version of the summary
        """
        if not openai.api_key:
            logger.warning("No OpenAI API key available. Returning original summary.")
            return f"{title}\n\n{summary}"
            
        try:
            # Create a prompt for the OpenAI API
            prompt = self._create_prompt(title, summary)
            
            # Call the OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a witty tech journalist specializing in AI news with a great sense of humor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            # Extract the generated text
            humorous_summary = response.choices[0].message.content.strip()
            
            return humorous_summary
            
        except Exception as e:
            logger.error(f"Error generating humorous summary: {str(e)}")
            return f"{title}\n\n{summary}"

    def _create_prompt(self, title: str, summary: str) -> str:
        """
        Create a prompt for the OpenAI API.

        Args:
            title: The title of the article
            summary: The summary of the article

        Returns:
            A prompt for the OpenAI API
        """
        return f"""
        Rewrite this AI news summary in a humorous, entertaining way:
        
        Title: {title}
        Summary: {summary}
        
        Make it witty, include some puns related to AI, and maintain all the key facts.
        Format as a short, funny news segment that would make people laugh while still being informative.
        """

    def batch_add_humor(
        self, articles: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Add humor to a batch of article summaries.

        Args:
            articles: List of article dictionaries with 'title' and 'summary' keys

        Returns:
            The same list with an added 'humorous_content' key for each article
        """
        for article in articles:
            if "title" in article and "summary" in article:
                article["humorous_content"] = self.add_humor(
                    article["title"], article["summary"]
                )
        
        return articles


def add_humor_to_articles(articles_data: Union[List[Dict], Dict]) -> Union[List[Dict], Dict]:
    """
    Add humor to articles from a list of dictionaries or a single dictionary.

    Args:
        articles_data: List of article dictionaries or a single article dictionary
                      Each article should have 'title' and 'summary' keys

    Returns:
        The same structure with an added 'humorous_content' key for each article
    """
    # Get configuration from environment variables
    model = os.getenv("HUMOR_MODEL", "gpt-4")
    temperature = float(os.getenv("HUMOR_TEMPERATURE", "0.7"))
    
    # Initialize humor generator
    humor_generator = HumorGenerator(
        model=model,
        temperature=temperature,
    )
    
    # Handle single article case
    if isinstance(articles_data, dict):
        if "title" in articles_data and "summary" in articles_data:
            articles_data["humorous_content"] = humor_generator.add_humor(
                articles_data["title"], articles_data["summary"]
            )
        return articles_data
    
    # Handle list of articles
    return humor_generator.batch_add_humor(articles_data)


def main():
    """Run the humor generator as a standalone module with a test summary."""
    test_title = "OpenAI Releases GPT-4 with Enhanced Capabilities"
    test_summary = """
    OpenAI has released GPT-4, a multimodal AI model that accepts image and text inputs and produces text outputs. 
    The model demonstrates human-level performance on various benchmarks and shows improved capabilities in problem-solving, 
    coding, and creative content generation. Despite these advancements, the model still has limitations including biases 
    and hallucinations. OpenAI continues to refine the model based on user feedback.
    """
    
    # Initialize humor generator with default settings
    humor_generator = HumorGenerator()
    
    # Generate humorous summary
    humorous_summary = humor_generator.add_humor(test_title, test_summary)
    
    # Print results
    print("Original title:")
    print(test_title)
    print("\nOriginal summary:")
    print(test_summary)
    print("\nHumorous summary:")
    print(humorous_summary)


if __name__ == "__main__":
    main() 
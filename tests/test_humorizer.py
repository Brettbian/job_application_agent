"""
Tests for the humor generation module.
"""
import unittest
from unittest.mock import MagicMock, patch

from src.news_summarizer.humor.humorizer import HumorGenerator


class TestHumorGenerator(unittest.TestCase):
    """Test cases for the HumorGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_title = "OpenAI Releases GPT-4 with Enhanced Capabilities"
        self.test_summary = """
        OpenAI has released GPT-4, a multimodal AI model that accepts image and text inputs and produces text outputs. 
        The model demonstrates human-level performance on various benchmarks and shows improved capabilities in problem-solving, 
        coding, and creative content generation. Despite these advancements, the model still has limitations including biases 
        and hallucinations. OpenAI continues to refine the model based on user feedback.
        """
        self.expected_humorous_content = """
        # GPT-4: The AI That's Smarter Than Your Ex's Comeback

        OpenAI just dropped GPT-4, and it's so smart it can not only finish your sentences but probably your tax returns too! 
        This multimodal marvel accepts both images and text, meaning it can now judge your fashion choices AND your grammar simultaneously.

        The model aces academic tests with flying colors, making it the first AI to be simultaneously accepted to Harvard, MIT, 
        and that one community college your cousin keeps talking about. It's particularly good at problem-solving, coding, 
        and generating content so creative it's making struggling writers consider career changes.

        Despite being trained on enough text to make every librarian jealous, GPT-4 still has its quirks - occasionally hallucinating 
        facts with the confidence of your uncle at Thanksgiving dinner. OpenAI admits the model isn't perfect, but they're working on it... 
        probably by making it read Twitter until it loses faith in humanity like the rest of us.
        """

    @patch("src.news_summarizer.humor.humorizer.openai.api_key", "test_api_key")
    @patch("src.news_summarizer.humor.humorizer.openai.ChatCompletion.create")
    def test_add_humor(self, mock_openai_create):
        """Test adding humor to a summary."""
        # Set up mock
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = self.expected_humorous_content
        mock_openai_create.return_value = mock_response
        
        # Create the humor generator
        humor_generator = HumorGenerator(
            model="gpt-4",
            temperature=0.7,
            max_tokens=500,
        )
        
        # Call the method
        humorous_content = humor_generator.add_humor(self.test_title, self.test_summary)
        
        # Assertions
        self.assertEqual(humorous_content, self.expected_humorous_content)
        mock_openai_create.assert_called_once()
        
        # Verify the prompt was created correctly
        _, kwargs = mock_openai_create.call_args
        self.assertEqual(kwargs["model"], "gpt-4")
        self.assertEqual(kwargs["temperature"], 0.7)
        self.assertEqual(kwargs["max_tokens"], 500)
        self.assertEqual(len(kwargs["messages"]), 2)
        self.assertEqual(kwargs["messages"][0]["role"], "system")
        self.assertEqual(kwargs["messages"][1]["role"], "user")

    @patch("src.news_summarizer.humor.humorizer.openai.api_key", None)
    def test_add_humor_no_api_key(self):
        """Test adding humor without an API key."""
        # Create the humor generator
        humor_generator = HumorGenerator()
        
        # Call the method
        humorous_content = humor_generator.add_humor(self.test_title, self.test_summary)
        
        # Assertions
        self.assertEqual(humorous_content, f"{self.test_title}\n\n{self.test_summary}")

    @patch("src.news_summarizer.humor.humorizer.openai.api_key", "test_api_key")
    @patch("src.news_summarizer.humor.humorizer.openai.ChatCompletion.create")
    def test_add_humor_api_error(self, mock_openai_create):
        """Test adding humor with an API error."""
        # Set up mock to raise an exception
        mock_openai_create.side_effect = Exception("API error")
        
        # Create the humor generator
        humor_generator = HumorGenerator()
        
        # Call the method
        humorous_content = humor_generator.add_humor(self.test_title, self.test_summary)
        
        # Assertions
        self.assertEqual(humorous_content, f"{self.test_title}\n\n{self.test_summary}")


if __name__ == "__main__":
    unittest.main() 
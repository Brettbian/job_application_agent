"""
Tests for the summarization module.
"""
import unittest
from unittest.mock import MagicMock, patch

import torch

from src.news_summarizer.summarization.summarizer import ArticleSummarizer


class TestArticleSummarizer(unittest.TestCase):
    """Test cases for the ArticleSummarizer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the model and tokenizer
        self.mock_model = MagicMock()
        self.mock_tokenizer = MagicMock()
        
        # Create a test article
        self.test_article = """
        Researchers at OpenAI have developed a new language model called GPT-4 that demonstrates 
        human-level performance on various professional and academic benchmarks. The model is a 
        multimodal system that can accept image and text inputs and produce text outputs. According 
        to the research paper, GPT-4 exhibits more capabilities in areas such as problem-solving, 
        coding, and creative content generation compared to its predecessors. The model was trained 
        on a massive dataset of text and code, allowing it to understand and generate human language 
        with remarkable accuracy. Despite these advancements, the researchers acknowledge that the 
        model still has limitations, including potential biases, hallucinations, and a limited context 
        window. OpenAI has implemented various safety measures to mitigate these issues and is 
        continuing to refine the model based on user feedback and ongoing research.
        """
        
        # Expected summary
        self.expected_summary = "OpenAI has developed GPT-4, a multimodal language model that shows human-level performance on various benchmarks. It has improved capabilities in problem-solving, coding, and creative content generation, but still has limitations like biases and hallucinations."

    @patch("src.news_summarizer.summarization.summarizer.PegasusTokenizer")
    @patch("src.news_summarizer.summarization.summarizer.PegasusForConditionalGeneration")
    @patch("src.news_summarizer.summarization.summarizer.torch.cuda.is_available", return_value=False)
    def test_summarize_with_pegasus(self, mock_cuda, mock_model_class, mock_tokenizer_class):
        """Test summarization with PEGASUS model."""
        # Set up mocks
        mock_model_instance = MagicMock()
        mock_tokenizer_instance = MagicMock()
        
        mock_model_class.from_pretrained.return_value = mock_model_instance
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock the tokenizer encode method
        mock_input_ids = MagicMock()
        mock_tokenizer_instance.return_value = {"input_ids": mock_input_ids}
        
        # Mock the model generate method
        mock_summary_ids = MagicMock()
        mock_model_instance.generate.return_value = [mock_summary_ids]
        
        # Mock the tokenizer decode method
        mock_tokenizer_instance.decode.return_value = self.expected_summary
        
        # Create the summarizer with mocked dependencies
        summarizer = ArticleSummarizer(
            model_name="google/pegasus-cnn_dailymail",
            min_length=50,
            max_length=150,
        )
        
        # Replace the loaded model and tokenizer with our mocks
        summarizer.model = mock_model_instance
        summarizer.tokenizer = mock_tokenizer_instance
        
        # Mock the to method to avoid the error
        mock_input = {"input_ids": torch.tensor([[1, 2, 3]])}
        mock_tokenizer_instance.side_effect = None
        mock_tokenizer_instance.return_value = None
        mock_tokenizer_instance.__call__.return_value = mock_input
        
        # Call the method
        summary = summarizer.summarize(self.test_article)
        
        # Assertions
        self.assertEqual(summary, self.expected_summary)
        mock_model_instance.generate.assert_called_once()
        mock_tokenizer_instance.decode.assert_called_once_with(mock_summary_ids, skip_special_tokens=True)

    @patch("src.news_summarizer.summarization.summarizer.pipeline")
    def test_summarize_with_pipeline(self, mock_pipeline):
        """Test summarization with Hugging Face pipeline."""
        # Set up mock
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance
        mock_pipeline_instance.return_value = [{"summary_text": self.expected_summary}]
        
        # Create the summarizer
        summarizer = ArticleSummarizer()
        
        # Replace the model and tokenizer with None to force using the pipeline
        summarizer.model = None
        summarizer.tokenizer = None
        summarizer.summarization_pipeline = mock_pipeline_instance
        
        # Call the method
        summary = summarizer.summarize(self.test_article)
        
        # Assertions
        self.assertEqual(summary, self.expected_summary)
        mock_pipeline_instance.assert_called_once()

    def test_empty_text(self):
        """Test summarization with empty text."""
        # Create the summarizer with mocked dependencies to avoid loading the model
        with patch("src.news_summarizer.summarization.summarizer.PegasusTokenizer"), \
             patch("src.news_summarizer.summarization.summarizer.PegasusForConditionalGeneration"), \
             patch("src.news_summarizer.summarization.summarizer.torch.cuda.is_available", return_value=False):
            
            summarizer = ArticleSummarizer()
            summarizer.model = None
            summarizer.tokenizer = None
            summarizer.summarization_pipeline = MagicMock()
            
            # Call the method with empty text
            summary = summarizer.summarize("")
            
            # Assertions
            self.assertEqual(summary, "")


if __name__ == "__main__":
    unittest.main() 
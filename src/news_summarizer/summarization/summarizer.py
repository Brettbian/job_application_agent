"""
Summarization module for creating concise summaries of news articles.
"""
import logging
import os
from typing import Dict, List, Optional, Union

import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer, pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """Class for summarizing news articles using transformer models."""

    def __init__(
        self,
        model_name: str = "google/pegasus-cnn_dailymail",
        min_length: int = 50,
        max_length: int = 150,
        use_gpu: bool = True,
    ):
        """
        Initialize the ArticleSummarizer.

        Args:
            model_name: Name of the pre-trained model to use
            min_length: Minimum length of the summary in tokens
            max_length: Maximum length of the summary in tokens
            use_gpu: Whether to use GPU for inference if available
        """
        self.model_name = model_name
        self.min_length = min_length
        self.max_length = max_length
        
        # Determine device
        self.device = "cuda" if torch.cuda.is_available() and use_gpu else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self._load_model()

    def _load_model(self):
        """Load the summarization model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = PegasusTokenizer.from_pretrained(self.model_name)
            self.model = PegasusForConditionalGeneration.from_pretrained(self.model_name).to(
                self.device
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fallback to simpler summarization pipeline
            logger.info("Falling back to default summarization pipeline")
            self.summarization_pipeline = pipeline("summarization", device=0 if self.device == "cuda" else -1)
            self.model = None
            self.tokenizer = None

    def summarize(self, text: str) -> str:
        """
        Generate a summary for the given text.

        Args:
            text: The text to summarize

        Returns:
            A summary of the text
        """
        if not text:
            logger.warning("Empty text provided for summarization")
            return ""
            
        try:
            # Truncate text if it's too long (model-specific limits)
            max_input_length = 1024  # This is a reasonable limit for most models
            if len(text.split()) > max_input_length:
                logger.warning(f"Text too long ({len(text.split())} words), truncating to {max_input_length} words")
                text = " ".join(text.split()[:max_input_length])
            
            # Use the loaded model if available, otherwise use the pipeline
            if self.model and self.tokenizer:
                return self._summarize_with_pegasus(text)
            else:
                return self._summarize_with_pipeline(text)
                
        except Exception as e:
            logger.error(f"Error during summarization: {str(e)}")
            # Return a truncated version of the original text as fallback
            return text[:500] + "..."

    def _summarize_with_pegasus(self, text: str) -> str:
        """
        Summarize text using the PEGASUS model.

        Args:
            text: The text to summarize

        Returns:
            A summary of the text
        """
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True).to(
            self.device
        )
        
        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=self.max_length,
            min_length=self.min_length,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def _summarize_with_pipeline(self, text: str) -> str:
        """
        Summarize text using the Hugging Face summarization pipeline.

        Args:
            text: The text to summarize

        Returns:
            A summary of the text
        """
        summary = self.summarization_pipeline(
            text,
            max_length=self.max_length,
            min_length=self.min_length,
            do_sample=False,
        )
        
        return summary[0]["summary_text"]

    def batch_summarize(self, texts: List[str]) -> List[str]:
        """
        Generate summaries for a batch of texts.

        Args:
            texts: List of texts to summarize

        Returns:
            List of summaries
        """
        return [self.summarize(text) for text in texts]


def summarize_articles(articles_data: Union[List[Dict], Dict]) -> Union[List[Dict], Dict]:
    """
    Summarize articles from a list of dictionaries or a single dictionary.

    Args:
        articles_data: List of article dictionaries or a single article dictionary
                      Each article should have a 'text' key

    Returns:
        The same structure with an added 'summary' key for each article
    """
    # Get configuration from environment variables
    model_name = os.getenv("SUMMARIZATION_MODEL", "google/pegasus-cnn_dailymail")
    min_length = int(os.getenv("SUMMARY_MIN_LENGTH", "50"))
    max_length = int(os.getenv("SUMMARY_MAX_LENGTH", "150"))
    
    # Initialize summarizer
    summarizer = ArticleSummarizer(
        model_name=model_name,
        min_length=min_length,
        max_length=max_length,
    )
    
    # Handle single article case
    if isinstance(articles_data, dict):
        if "text" in articles_data:
            articles_data["summary"] = summarizer.summarize(articles_data["text"])
        return articles_data
    
    # Handle list of articles
    for article in articles_data:
        if "text" in article:
            article["summary"] = summarizer.summarize(article["text"])
    
    return articles_data


def main():
    """Run the summarizer as a standalone module with a test article."""
    test_article = """
    Researchers at OpenAI have developed a new language model called GPT-4 that demonstrates human-level performance on various professional and academic benchmarks. The model is a multimodal system that can accept image and text inputs and produce text outputs. According to the research paper, GPT-4 exhibits more capabilities in areas such as problem-solving, coding, and creative content generation compared to its predecessors. The model was trained on a massive dataset of text and code, allowing it to understand and generate human language with remarkable accuracy. Despite these advancements, the researchers acknowledge that the model still has limitations, including potential biases, hallucinations, and a limited context window. OpenAI has implemented various safety measures to mitigate these issues and is continuing to refine the model based on user feedback and ongoing research.
    """
    
    # Initialize summarizer with default settings
    summarizer = ArticleSummarizer()
    
    # Generate summary
    summary = summarizer.summarize(test_article)
    
    # Print results
    print("Original text:")
    print(test_article)
    print("\nSummary:")
    print(summary)


if __name__ == "__main__":
    main() 
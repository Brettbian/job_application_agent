"""
Entry point for the AI News Summarizer application.
"""
import sys

from src.news_summarizer.main import main as news_summarizer_main


def main():
    """Run the AI News Summarizer application."""
    print("Hello from AI News Summarizer!")
    return news_summarizer_main()


if __name__ == "__main__":
    sys.exit(main())

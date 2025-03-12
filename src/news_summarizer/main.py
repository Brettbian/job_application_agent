"""
Main module for the AI News Summarizer.

This module orchestrates the entire process:
1. Collect news from various sources
2. Summarize the articles
3. Add humor to the summaries
4. Format and save the results
"""
import logging
import os
import sys
from typing import Dict, List, Optional

import pandas as pd

from src.news_summarizer.data_collection.collector import NewsCollector
from src.news_summarizer.humor.humorizer import HumorGenerator
from src.news_summarizer.summarization.summarizer import ArticleSummarizer
from src.news_summarizer.utils.config import load_config
from src.news_summarizer.utils.formatter import NewsletterFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def collect_news(config) -> pd.DataFrame:
    """
    Collect news from various sources.

    Args:
        config: Configuration object

    Returns:
        DataFrame containing collected articles
    """
    logger.info("Collecting news...")
    
    collector = NewsCollector(
        max_articles_per_source=config.get("max_articles_per_source"),
        days_to_look_back=config.get("days_to_look_back"),
    )
    
    articles_df = collector.collect_news()
    
    if articles_df.empty:
        logger.warning("No articles collected")
    else:
        logger.info(f"Collected {len(articles_df)} articles")
    
    return articles_df


def summarize_articles(articles_df: pd.DataFrame, config) -> pd.DataFrame:
    """
    Summarize the collected articles.

    Args:
        articles_df: DataFrame containing collected articles
        config: Configuration object

    Returns:
        DataFrame with added 'summary' column
    """
    if articles_df.empty:
        return articles_df
    
    logger.info("Summarizing articles...")
    
    summarizer = ArticleSummarizer(
        model_name=config.get("summarization_model"),
        min_length=config.get("summary_min_length"),
        max_length=config.get("summary_max_length"),
    )
    
    # Apply summarization to each article
    articles_df["summary"] = articles_df["text"].apply(summarizer.summarize)
    
    logger.info("Articles summarized successfully")
    
    return articles_df


def add_humor(articles_df: pd.DataFrame, config) -> pd.DataFrame:
    """
    Add humor to the summarized articles.

    Args:
        articles_df: DataFrame containing summarized articles
        config: Configuration object

    Returns:
        DataFrame with added 'humorous_content' column
    """
    if articles_df.empty:
        return articles_df
    
    logger.info("Adding humor to summaries...")
    
    humor_generator = HumorGenerator(
        model=config.get("humor_model"),
        temperature=config.get("humor_temperature"),
    )
    
    # Apply humor generation to each article
    articles_df["humorous_content"] = articles_df.apply(
        lambda row: humor_generator.add_humor(row["title"], row["summary"]),
        axis=1,
    )
    
    logger.info("Humor added successfully")
    
    return articles_df


def format_and_save(articles_df: pd.DataFrame, config) -> Optional[str]:
    """
    Format and save the results.

    Args:
        articles_df: DataFrame containing articles with humor
        config: Configuration object

    Returns:
        Path to the saved file or None if no articles
    """
    if articles_df.empty:
        logger.warning("No articles to format and save")
        return None
    
    logger.info("Formatting and saving results...")
    
    formatter = NewsletterFormatter(
        output_format=config.get("output_format"),
        output_directory=config.get("output_directory"),
    )
    
    # Convert DataFrame to list of dictionaries
    articles_list = articles_df.to_dict("records")
    
    # Format newsletter
    newsletter_content = formatter.format_newsletter(articles_list)
    
    # Save newsletter
    filepath = formatter.save_newsletter(newsletter_content)
    
    if filepath:
        logger.info(f"Newsletter saved to {filepath}")
    else:
        logger.error("Failed to save newsletter")
    
    return filepath


def main():
    """Run the AI News Summarizer."""
    try:
        # Load configuration
        config = load_config()
        
        # Collect news
        articles_df = collect_news(config)
        
        if articles_df.empty:
            logger.error("No articles collected. Exiting.")
            return 1
        
        # Summarize articles
        articles_df = summarize_articles(articles_df, config)
        
        # Add humor
        articles_df = add_humor(articles_df, config)
        
        # Format and save
        filepath = format_and_save(articles_df, config)
        
        if filepath:
            logger.info(f"AI News Summarizer completed successfully. Output saved to {filepath}")
            return 0
        else:
            logger.error("AI News Summarizer failed to produce output")
            return 1
            
    except Exception as e:
        logger.exception(f"Error running AI News Summarizer: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
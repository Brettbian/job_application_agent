"""
News collector module for gathering AI news from various sources.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from newspaper.article import ArticleException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Top AI news sources based on quality and relevance
AI_NEWS_SOURCES = [
    {
        "name": "Analytics Insight",
        "url": "https://www.analyticsinsight.net/category/artificial-intelligence/",
    },
    {"name": "AI Magazine", "url": "https://aimagazine.com/latest-news"},
    {"name": "DevX", "url": "https://www.devx.com/category/ai/"},
    {"name": "MIT News", "url": "https://news.mit.edu/topic/artificial-intelligence2"},
    {
        "name": "Science Daily",
        "url": "https://www.sciencedaily.com/news/computers_math/artificial_intelligence/",
    },
    {"name": "Google AI Blog", "url": "https://ai.google/latest-news/"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/"},
]


class NewsCollector:
    """Class for collecting AI news from various sources."""

    def __init__(
        self,
        sources: List[Dict[str, str]] = AI_NEWS_SOURCES,
        max_articles_per_source: int = 5,
        days_to_look_back: int = 3,
    ):
        """
        Initialize the NewsCollector.

        Args:
            sources: List of dictionaries containing news sources with 'name' and 'url' keys
            max_articles_per_source: Maximum number of articles to collect per source
            days_to_look_back: Number of days to look back for articles
        """
        self.sources = sources
        self.max_articles_per_source = max_articles_per_source
        self.days_to_look_back = days_to_look_back
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def collect_news(self) -> pd.DataFrame:
        """
        Collect news from all sources.

        Returns:
            DataFrame containing collected articles with columns:
            - title: Article title
            - text: Article text content
            - url: Article URL
            - source: Source name
            - date: Publication date
        """
        articles_data = []
        
        for source in self.sources:
            try:
                logger.info(f"Collecting news from {source['name']}...")
                source_articles = self._collect_from_source(source)
                articles_data.extend(source_articles)
                logger.info(f"Collected {len(source_articles)} articles from {source['name']}")
            except Exception as e:
                logger.error(f"Error collecting from {source['name']}: {str(e)}")
        
        # Convert to DataFrame and filter by date
        if not articles_data:
            logger.warning("No articles collected from any source")
            return pd.DataFrame()
        
        df = pd.DataFrame(articles_data)
        
        # Filter by date if we have date information
        if "date" in df.columns:
            cutoff_date = datetime.now() - timedelta(days=self.days_to_look_back)
            df = df[df["date"] >= cutoff_date]
        
        return df

    def _collect_from_source(self, source: Dict[str, str]) -> List[Dict]:
        """
        Collect articles from a specific source.

        Args:
            source: Dictionary with 'name' and 'url' keys

        Returns:
            List of article dictionaries
        """
        articles = []
        try:
            response = requests.get(source["url"], headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract article URLs (this will need customization for each source)
            article_links = self._extract_article_links(soup, source["url"])
            
            # Limit the number of articles
            article_links = article_links[:self.max_articles_per_source]
            
            # Extract content from each article
            for url in article_links:
                try:
                    article_data = self._extract_article_content(url, source["name"])
                    if article_data:
                        articles.append(article_data)
                except Exception as e:
                    logger.error(f"Error extracting content from {url}: {str(e)}")
        
        except requests.RequestException as e:
            logger.error(f"Request error for {source['name']}: {str(e)}")
        
        return articles

    def _extract_article_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract article links from a BeautifulSoup object.
        
        This is a generic implementation that will need customization for specific sources.

        Args:
            soup: BeautifulSoup object of the source page
            base_url: Base URL of the source

        Returns:
            List of article URLs
        """
        links = []
        
        # Find all <a> tags that might be article links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            
            # Skip if it's not an article link (customize this for each source)
            if not href or href.startswith("#") or "javascript:" in href:
                continue
                
            # Make relative URLs absolute
            if href.startswith("/"):
                # Extract domain from base_url
                domain = "/".join(base_url.split("/")[:3])  # http(s)://domain.com
                href = domain + href
            elif not href.startswith(("http://", "https://")):
                href = base_url.rstrip("/") + "/" + href.lstrip("/")
                
            links.append(href)
            
        # Remove duplicates while preserving order
        unique_links = []
        for link in links:
            if link not in unique_links:
                unique_links.append(link)
                
        return unique_links

    def _extract_article_content(
        self, url: str, source_name: str
    ) -> Optional[Dict[str, str]]:
        """
        Extract content from an article URL.

        Args:
            url: Article URL
            source_name: Name of the source

        Returns:
            Dictionary with article data or None if extraction failed
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            # Skip articles without title or text
            if not article.title or not article.text:
                logger.warning(f"Skipping article with missing title or text: {url}")
                return None
                
            return {
                "title": article.title,
                "text": article.text,
                "url": url,
                "source": source_name,
                "date": article.publish_date or datetime.now(),
            }
        except ArticleException as e:
            logger.error(f"Article extraction error for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting from {url}: {str(e)}")
            return None


def main():
    """Run the news collector as a standalone module."""
    # Get configuration from environment variables
    max_articles = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "5"))
    days_back = int(os.getenv("DAYS_TO_LOOK_BACK", "3"))
    
    collector = NewsCollector(
        max_articles_per_source=max_articles,
        days_to_look_back=days_back,
    )
    
    articles_df = collector.collect_news()
    
    if articles_df.empty:
        logger.warning("No articles collected")
        return
        
    logger.info(f"Collected {len(articles_df)} articles")
    
    # Print a summary of collected articles
    for _, row in articles_df.iterrows():
        logger.info(f"Title: {row['title']}")
        logger.info(f"Source: {row['source']}")
        logger.info(f"URL: {row['url']}")
        logger.info("-" * 50)


if __name__ == "__main__":
    main() 
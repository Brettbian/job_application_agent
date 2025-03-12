"""
Formatter module for creating nicely formatted output from the summarized and humorized articles.
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class NewsletterFormatter:
    """Class for formatting articles into a newsletter."""

    def __init__(
        self,
        output_format: str = "markdown",
        output_directory: str = "./output",
    ):
        """
        Initialize the NewsletterFormatter.

        Args:
            output_format: The format of the output (markdown or html)
            output_directory: The directory to save the output to
        """
        self.output_format = output_format.lower()
        self.output_directory = output_directory
        
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

    def format_newsletter(self, articles: List[Dict]) -> str:
        """
        Format articles into a newsletter.

        Args:
            articles: List of article dictionaries with 'title', 'humorous_content', 'url', and 'source' keys

        Returns:
            Formatted newsletter as a string
        """
        if self.output_format == "markdown":
            return self._format_markdown(articles)
        elif self.output_format == "html":
            return self._format_html(articles)
        else:
            logger.warning(f"Unsupported output format: {self.output_format}. Defaulting to markdown.")
            return self._format_markdown(articles)

    def _format_markdown(self, articles: List[Dict]) -> str:
        """
        Format articles into a markdown newsletter.

        Args:
            articles: List of article dictionaries

        Returns:
            Markdown formatted newsletter
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        newsletter = f"# AI News with a Twist - {current_date}\n\n"
        
        for article in articles:
            if "humorous_content" in article:
                newsletter += f"## {article.get('title', 'Untitled Article')}\n\n"
                newsletter += f"{article['humorous_content']}\n\n"
                
                # Add source information
                if "url" in article and "source" in article:
                    newsletter += f"*Source: [{article['source']}]({article['url']})*\n\n"
                
                newsletter += "---\n\n"
        
        # Add footer
        newsletter += f"\n\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by AI News Summarizer*"
        
        return newsletter

    def _format_html(self, articles: List[Dict]) -> str:
        """
        Format articles into an HTML newsletter.

        Args:
            articles: List of article dictionaries

        Returns:
            HTML formatted newsletter
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI News with a Twist - {current_date}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                }}
                h2 {{
                    color: #3498db;
                }}
                .article {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .source {{
                    font-style: italic;
                    color: #7f8c8d;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 0.8em;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <h1>AI News with a Twist - {current_date}</h1>
        """
        
        for article in articles:
            if "humorous_content" in article:
                # Replace newlines with <br> tags
                content = article['humorous_content'].replace('\n', '<br>')
                
                html += f"""
                <div class="article">
                    <h2>{article.get('title', 'Untitled Article')}</h2>
                    <div class="content">
                        {content}
                    </div>
                """
                
                # Add source information
                if "url" in article and "source" in article:
                    html += f"""
                    <p class="source">
                        Source: <a href="{article['url']}" target="_blank">{article['source']}</a>
                    </p>
                    """
                
                html += "</div>"
        
        # Add footer
        html += f"""
            <div class="footer">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by AI News Summarizer
            </div>
        </body>
        </html>
        """
        
        return html

    def save_newsletter(self, content: str) -> str:
        """
        Save the newsletter to a file.

        Args:
            content: The newsletter content

        Returns:
            The path to the saved file
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        extension = ".md" if self.output_format == "markdown" else ".html"
        
        filename = f"ai_news_{current_date}{extension}"
        filepath = os.path.join(self.output_directory, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"Newsletter saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving newsletter: {str(e)}")
            return ""


def format_and_save_newsletter(articles: List[Dict]) -> str:
    """
    Format and save a newsletter from the given articles.

    Args:
        articles: List of article dictionaries

    Returns:
        The path to the saved newsletter file
    """
    # Get configuration from environment variables
    output_format = os.getenv("OUTPUT_FORMAT", "markdown")
    output_directory = os.getenv("OUTPUT_DIRECTORY", "./output")
    
    # Initialize formatter
    formatter = NewsletterFormatter(
        output_format=output_format,
        output_directory=output_directory,
    )
    
    # Format newsletter
    newsletter_content = formatter.format_newsletter(articles)
    
    # Save newsletter
    return formatter.save_newsletter(newsletter_content)


def main():
    """Run the formatter as a standalone module with test articles."""
    test_articles = [
        {
            "title": "OpenAI Releases GPT-4 with Enhanced Capabilities",
            "humorous_content": """
            # GPT-4: The AI That's Smarter Than Your Ex's Comeback

            OpenAI just dropped GPT-4, and it's so smart it can not only finish your sentences but probably your tax returns too! This multimodal marvel accepts both images and text, meaning it can now judge your fashion choices AND your grammar simultaneously.

            The model aces academic tests with flying colors, making it the first AI to be simultaneously accepted to Harvard, MIT, and that one community college your cousin keeps talking about. It's particularly good at problem-solving, coding, and generating content so creative it's making struggling writers consider career changes.

            Despite being trained on enough text to make every librarian jealous, GPT-4 still has its quirks - occasionally hallucinating facts with the confidence of your uncle at Thanksgiving dinner. OpenAI admits the model isn't perfect, but they're working on it... probably by making it read Twitter until it loses faith in humanity like the rest of us.

            Remember folks, it may be smart, but it still can't load the dishwasher correctly - some tasks remain uniquely human!
            """,
            "url": "https://openai.com/blog/gpt-4",
            "source": "OpenAI Blog",
        },
        {
            "title": "Google Introduces New AI Features for Search",
            "humorous_content": """
            # Google Search Gets AI Upgrade: Now Finds Your Lost Socks Too!

            Google has announced new AI features for its search engine, promising to understand your vague queries almost as well as your therapist does. The new system can now interpret natural language questions, even when you type "that movie with the guy who does the thing" at 2 AM.

            Using advanced machine learning algorithms that would make Einstein scratch his head, Google Search now provides more relevant results and summaries that are actually useful - a technological achievement on par with landing on the moon, if the moon were made of information.

            "We've trained our AI to understand context better than most humans understand their dating app matches," said a Google spokesperson, who then demonstrated by searching "why is my plant sad" and receiving detailed diagnostics instead of existential philosophy.

            The AI can also generate custom responses that adapt to your search history, meaning it knows you're not really going to make that complicated recipe you just looked up. It just knows.

            Privacy advocates express concern that the AI might be getting too smart, citing fears that it will eventually start answering the questions you're too afraid to ask. Google assures users that the AI has been programmed with just enough emotional intelligence to be helpful, but not enough to judge you for searching "is cereal soup" at midnight.
            """,
            "url": "https://blog.google/products/search/search-ai-features",
            "source": "Google Blog",
        },
    ]
    
    # Format and save newsletter
    filepath = format_and_save_newsletter(test_articles)
    
    # Print results
    if filepath:
        print(f"Newsletter saved to {filepath}")
        
        # Print the content of the file
        with open(filepath, "r", encoding="utf-8") as f:
            print("\nNewsletter content:")
            print(f.read())


if __name__ == "__main__":
    main() 
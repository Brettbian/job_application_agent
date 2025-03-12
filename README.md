# AI News Summarizer with Humor

An automated system that collects, summarizes, and adds humor to the latest AI news.

## Features

- Collects news from top AI publications
- Extracts and preprocesses article content
- Summarizes articles using state-of-the-art AI models
- Adds humor to summaries using specialized AI techniques
- Generates a formatted newsletter with the humorous summaries

## Project Structure

```
ai-news-summarizer/
├── src/
│   └── news_summarizer/
│       ├── data_collection/  # News collection modules
│       ├── summarization/    # Text summarization modules
│       ├── humor/            # Humor generation modules
│       └── utils/            # Utility functions
├── tests/                    # Test modules
├── .env.example              # Example environment variables
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-news-summarizer.git
cd ai-news-summarizer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package and dependencies:
```bash
pip install -e .
```

4. Create a `.env` file with your API keys (see `.env.example`).

## Usage

Run the main script to generate a humorous AI news summary:

```bash
python -m src.news_summarizer.main
```

The generated summary will be saved as a markdown file in the current directory.

## Configuration

You can configure the news sources, summarization model, and humor settings in the `.env` file.

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black .
isort .
```

## License

MIT

## Acknowledgements

This project uses several open-source libraries and AI models:
- newspaper3k for article extraction
- transformers for text summarization
- OpenAI API for humor generation

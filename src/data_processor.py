from typing import List, Dict, Any
from src.logger_setup import get_logger

logger = get_logger(__name__)

def filter_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filters the list of fetched articles.

    Current filters:
    - Removes articles with missing or empty title or description.
    - (Optional) Add more filters here later (e.g., deduplication, source filtering).
    """
    filtered_list = []
    seen_urls = set() # Basic deduplication based on URL

    for article in articles:
        title = article.get("title")
        description = article.get("description")
        url = article.get("url")

        # 1. Check for essential content
        if not title or not description:
            logger.debug(f"Filtering out article due to missing title/description: {title[:50]}...")
            continue

        # 2. Check for duplicates based on URL
        if url in seen_urls:
            logger.debug(f"Filtering out duplicate article URL: {url}")
            continue
        if url:
             seen_urls.add(url)

        # If checks pass, add to filtered list
        filtered_list.append(article)

    original_count = len(articles)
    filtered_count = len(filtered_list)
    if original_count != filtered_count:
        logger.info(f"Filtered {original_count - filtered_count} articles (missing content/duplicates). Retaining {filtered_count}.")
    else:
        logger.info("No articles filtered out.")

    return filtered_list

# Example usage (optional)
if __name__ == "__main__":
    from src.logger_setup import setup_logging
    setup_logging()

    sample_articles = [
        {"symbol": "AAPL", "title": "Apple announce new product", "description": "Details inside.", "url": "http://example.com/1"},
        {"symbol": "MSFT", "title": "", "description": "Microsoft earnings call.", "url": "http://example.com/2"},
        {"symbol": "GOOG", "title": "Google results", "description": None, "url": "http://example.com/3"},
        {"symbol": "TSLA", "title": "Tesla news", "description": "Elon speaks again.", "url": "http://example.com/4"},
        {"symbol": "AAPL", "title": "Apple announce new product", "description": "Details inside.", "url": "http://example.com/1"}, # Duplicate URL
        {"symbol": "NVDA", "title": "Nvidia gains", "description": "Stock price soaring.", "url": "http://example.com/5"},
    ]
    logger.info(f"Original articles: {len(sample_articles)}")
    filtered = filter_articles(sample_articles)
    logger.info(f"Filtered articles: {len(filtered)}")
    logger.info(filtered) 
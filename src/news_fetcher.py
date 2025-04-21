import httpx
import asyncio
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from src.config_loader import get_config
from src.logger_setup import get_logger
from src.watchlist import get_watchlist

logger = get_logger(__name__)

NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

async def fetch_news_for_symbol(symbol: str, api_key: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
    """Fetches news articles for a specific symbol from NewsAPI.org."""
    articles_list = []
    # Fetch news from the last N hours (e.g., 24 hours) to keep it recent
    # NewsAPI free tier might limit how far back you can go
    from_datetime = (datetime.utcnow() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "q": symbol, # Use the symbol as the query term
        "apiKey": api_key,
        "language": "en",
        "sortBy": "publishedAt", # Get the latest news first
        "pageSize": 20, # Limit the number of results per symbol (adjust as needed)
        "from": from_datetime
    }

    print(f"Fetching news for symbol '{symbol}' from NewsAPI...", file=sys.stderr)
    
    try:
        print(f"Making request to {NEWS_API_BASE_URL} for symbol '{symbol}'", file=sys.stderr)
        response = await client.get(NEWS_API_BASE_URL, params=params)
        
        print(f"Got response for '{symbol}', status: {response.status_code}", file=sys.stderr)
        
        if response.status_code != 200:
            print(f"ERROR {response.status_code} for '{symbol}': {response.text}", file=sys.stderr)
            
        response.raise_for_status() # Raise exception for 4xx or 5xx errors

        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            print(f"SUCCESS: Fetched {len(articles)} articles for symbol '{symbol}'", file=sys.stderr)
            # Extract relevant fields
            for article in articles:
                articles_list.append({
                    "symbol": symbol, # Add the queried symbol for context
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "source": article.get("source", {}).get("name")
                })
        elif data.get("status") == "error":
            print(f"API ERROR for '{symbol}': {data.get('code')} - {data.get('message')}", file=sys.stderr)
            # Specific handling for common errors
            if data.get('code') == 'rateLimited':
                print(f"Rate limit exceeded for '{symbol}'", file=sys.stderr)
            elif data.get('code') == 'apiKeyInvalid' or data.get('code') == 'apiKeyMissing':
                print(f"Invalid or missing API key for '{symbol}'. Check config/.env", file=sys.stderr)
        else:
            print(f"Unexpected status from NewsAPI for '{symbol}': {data.get('status')}", file=sys.stderr)

    except httpx.HTTPStatusError as e:
        print(f"HTTP error fetching news for '{symbol}': {e.response.status_code} - {e.response.text}", file=sys.stderr)
    except httpx.RequestError as e:
        print(f"Network error fetching news for '{symbol}': {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error fetching news for '{symbol}': {e}", file=sys.stderr)

    return articles_list

async def fetch_news_for_watchlist() -> List[Dict[str, Any]]:
    """Fetches news for all symbols in the watchlist concurrently."""
    config = get_config()
    api_key = config.get("news_api_key")
    watchlist = get_watchlist()
    all_articles = []

    if not api_key:
        logger.error("NewsAPI key not found in configuration. Cannot fetch news.")
        return []

    # Add debug logging to show the API key is being loaded (masked)
    key_preview = api_key[:4] + "..." if api_key and len(api_key) > 4 else "None"
    logger.info(f"Using NewsAPI key starting with: {key_preview}")

    if not watchlist:
        logger.warning("Watchlist is empty. No news to fetch.")
        return []
    
    logger.info(f"Fetching news for watchlist: {watchlist}")

    # Use a shared httpx client for connection pooling
    async with httpx.AsyncClient(timeout=20.0) as client: # Increased timeout
        tasks = [fetch_news_for_symbol(symbol, api_key, client) for symbol in watchlist]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, list):
                symbol = watchlist[i] if i < len(watchlist) else "unknown"
                logger.info(f"Found {len(result)} articles for {symbol}")
                all_articles.extend(result)
            elif isinstance(result, Exception):
                symbol = watchlist[i] if i < len(watchlist) else "unknown"
                logger.error(f"Error gathering news results for {symbol}: {result}")
            # Individual errors within fetch_news_for_symbol are logged there

    logger.info(f"Fetched a total of {len(all_articles)} articles for the watchlist.")
    return all_articles

# Example usage (optional)
if __name__ == "__main__":
    from src.logger_setup import setup_logging
    setup_logging() # Initialize logging for standalone run

    async def run_fetcher():
        logger.info("--- Running News Fetcher Standalone --- ")
        # Ensure you have a config/.env file with NEWS_API_KEY and WATCHLIST_SYMBOLS
        # Example: WATCHLIST_SYMBOLS="TSLA,AAPL"
        articles = await fetch_news_for_watchlist()
        if articles:
            logger.info(f"Successfully fetched {len(articles)} articles.")
            # Print first few articles for verification
            for i, article in enumerate(articles[:3]):
                logger.info(f"Article {i+1}: {article['symbol']} - {article['title']}")
        else:
            logger.warning("No articles fetched.")
        logger.info("--- Finished News Fetcher Standalone --- ")

    asyncio.run(run_fetcher()) 
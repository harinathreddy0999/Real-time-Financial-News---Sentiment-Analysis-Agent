import asyncio
import time
import json # Import json library
import os # Import os for path operations
from typing import Dict, Any, List
import sys  # Import sys for stdout writing

# Diagnostic prints that don't rely on logging system
print("--- Starting Financial News Agent ---", file=sys.stderr)

try:
    from src.logger_setup import setup_logging, get_logger
    from src.config_loader import get_config
    from src.watchlist import get_watchlist
    from src.news_fetcher import fetch_news_for_watchlist
    from src.data_processor import filter_articles
    from src.llm_service import (
        summarize_text,
        analyze_sentiment,
        extract_topic,
        get_llm_service_instance # To check if LLM is available
    )
    from src.alerting_service import send_slack_alert # Import the alert function
    print("--- All modules imported successfully ---", file=sys.stderr)
except Exception as e:
    print(f"ERROR IMPORTING MODULES: {e}", file=sys.stderr)
    raise

# Initialize logging (try with direct print if logger fails)
try:
    setup_logging()
    logger = get_logger(__name__) # Get a logger for this module
    print("--- Logging initialized ---", file=sys.stderr)
except Exception as e:
    print(f"ERROR SETTING UP LOGGING: {e}", file=sys.stderr)
    # Continue anyway with print statements

# --- Configuration --- #
FETCH_INTERVAL_SECONDS = 15 * 60 # Default: 15 minutes (Adjustable via config later if needed)
PROCESS_BATCH_SIZE = 5 # Process N articles concurrently to avoid overwhelming LLM/API

async def process_single_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """Processes a single article using LLM services."""
    logger.debug(f"Processing article: {article.get('url')}")
    text_to_process = f"{article.get('title', '')}\n{article.get('description', '')}"

    # Ensure text is not empty
    if not text_to_process.strip():
        logger.warning(f"Article has no text content to process: {article.get('url')}")
        return article # Return original article, maybe mark as failed later

    # Use asyncio.gather to run LLM tasks concurrently for one article
    try:
        summary_task = summarize_text(text_to_process)
        sentiment_task = analyze_sentiment(text_to_process)
        topic_task = extract_topic(text_to_process)

        summary, sentiment, topic = await asyncio.gather(
            summary_task,
            sentiment_task,
            topic_task,
            return_exceptions=True # Capture exceptions instead of stopping gather
        )

        # Check results and handle potential exceptions from gather
        article["summary"] = summary if not isinstance(summary, Exception) else f"Error: {summary}"
        article["sentiment"] = sentiment if not isinstance(sentiment, Exception) else f"Error: {sentiment}"
        article["topic"] = topic if not isinstance(topic, Exception) else f"Error: {topic}"

        # Log errors explicitly if they occurred
        if isinstance(summary, Exception): logger.error(f"Summarization failed for {article.get('url')}: {summary}")
        if isinstance(sentiment, Exception): logger.error(f"Sentiment analysis failed for {article.get('url')}: {sentiment}")
        if isinstance(topic, Exception): logger.error(f"Topic extraction failed for {article.get('url')}: {topic}")

    except Exception as e:
        logger.exception(f"Unexpected error processing article {article.get('url')}: {e}")
        article["processing_error"] = str(e)

    logger.debug(f"Finished processing article: {article.get('url')}")
    return article

async def trigger_alert_if_needed(article: Dict[str, Any]):
    """Checks article sentiment and sends a Slack alert if non-Neutral."""
    sentiment = article.get("sentiment")
    # Check if sentiment is valid and not Neutral (also exclude errors)
    if sentiment and sentiment in ["Positive", "Negative"]:
        logger.info(f"Significant sentiment ({sentiment}) detected for {article.get('symbol')}. Triggering alert.")

        # Format message using Slack Block Kit
        title = article.get('title', 'N/A')
        summary = article.get('summary', 'N/A')
        topic = article.get('topic', 'N/A')
        url = article.get('url', '#')
        symbol = article.get('symbol', 'N/A')
        source = article.get('source', 'N/A')
        published_at = article.get('published_at', 'N/A')

        # Determine color based on sentiment
        color = "#36a64f" if sentiment == "Positive" else "#ff0000" # Green for Positive, Red for Negative

        alert_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{sentiment} Sentiment Alert: {symbol} ({topic})",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Symbol:*\n{symbol}"},
                    {"type": "mrkdwn", "text": f"*Detected Topic:*\n{topic}"},
                    {"type": "mrkdwn", "text": f"*Source:*\n{source}"},
                    {"type": "mrkdwn", "text": f"*Published:*\n{published_at}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Title:*\n<{url}|{title}>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary}"
                }
            }
            # Consider adding a divider or context block
            # { "type": "divider" }
        ]

        # Add a colored attachment bar (using attachments, a slightly older but effective way)
        # Note: Slack recommends Block Kit, but colored bars are easier with attachments.
        # For a pure Block Kit approach, you might use colored emoji or section backgrounds if supported.
        alert_attachments = [
            {
                "color": color,
                "blocks": alert_blocks # Put the main blocks inside the attachment for color
            }
        ]

        fallback_text = f"[{sentiment}] {symbol} ({topic}): {title} - {url}"

        # Send the alert (using attachments for the color bar)
        # send_slack_alert(text=fallback_text, blocks=alert_blocks) # Original block-only send
        await asyncio.to_thread(send_slack_alert, text=fallback_text, blocks=alert_attachments) # Use attachments
        # Note: Using asyncio.to_thread as slack_sdk's send is synchronous

    elif sentiment and sentiment.startswith("Error:"):
         logger.warning(f"Skipping alert for {article.get('symbol')} due to sentiment analysis error.")

async def save_processed_article(article: Dict[str, Any], file_path: str):
    """Appends a processed article dictionary to a JSON Lines file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Append the article as a JSON line
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False)
            f.write('\n') # Add newline to separate JSON objects
        logger.debug(f"Saved processed article to {file_path}: {article.get('url')}")
    except IOError as e:
        logger.error(f"Error writing processed article to {file_path}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error saving article {article.get('url')} to {file_path}: {e}")

async def main_agent_loop():
    """The main asynchronous loop for the financial news agent."""
    print("Initializing Financial News Agent...", file=sys.stderr)
    
    try:
        config = get_config()
        print(f"Config loaded successfully", file=sys.stderr)
    except Exception as e:
        print(f"ERROR LOADING CONFIG: {e}", file=sys.stderr)
        return
        
    try:
        watchlist = get_watchlist()
        print(f"Watchlist loaded: {watchlist}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR LOADING WATCHLIST: {e}", file=sys.stderr)
        return

    if not watchlist:
        print("Watchlist is empty. Agent cannot proceed. Exiting.", file=sys.stderr)
        return

    # Check if LLM is configured and available before starting loop
    try:
        llm_service = get_llm_service_instance()
        if not llm_service or not llm_service.client:
            print("LLM Service is not available (check API key?). Agent cannot process articles. Exiting.", file=sys.stderr)
            return
        print("LLM Service initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"ERROR INITIALIZING LLM SERVICE: {e}", file=sys.stderr)
        return

    # Define output file path
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(os.path.dirname(project_root), 'data', 'processed_news.jsonl')
    print(f"Will save articles to: {output_file}", file=sys.stderr)
    
    # Create path if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Agent started. Watchlist: {watchlist}. Fetch interval: {FETCH_INTERVAL_SECONDS} seconds.", file=sys.stderr)

    while True:
        start_time = time.monotonic()
        print("--- Starting new fetch cycle --- ", file=sys.stderr)

        try:
            # 1. Fetch News
            print("Fetching news for watchlist...", file=sys.stderr)
            raw_articles = await fetch_news_for_watchlist()
            print(f"Fetched {len(raw_articles)} raw articles.", file=sys.stderr)

            # 2. Filter News
            print(f"Filtering {len(raw_articles)} raw articles...", file=sys.stderr)
            filtered_articles = filter_articles(raw_articles)
            print(f"After filtering: {len(filtered_articles)} articles remain.", file=sys.stderr)

            # 3. Process News (Batching)
            if filtered_articles:
                print(f"Processing {len(filtered_articles)} filtered articles with LLM...", file=sys.stderr)
                processed_articles = []
                for i in range(0, len(filtered_articles), PROCESS_BATCH_SIZE):
                    batch = filtered_articles[i:i + PROCESS_BATCH_SIZE]
                    print(f"Processing batch {i//PROCESS_BATCH_SIZE + 1} of {len(batch)} articles.", file=sys.stderr)
                    tasks = [process_single_article(article) for article in batch]
                    results = await asyncio.gather(*tasks)
                    processed_articles.extend(results)
                    print(f"Batch {i//PROCESS_BATCH_SIZE + 1} processing complete.", file=sys.stderr)

                # 4. Output/Handle Results, Trigger Alerts, and Save Data
                print("--- Processing Complete, Saving Results --- ", file=sys.stderr)
                alert_tasks = []
                save_tasks = [] # Collect save tasks
                for article in processed_articles:
                    # Basic debugging output
                    print(f"Processed: {article.get('symbol')}, Sentiment: {article.get('sentiment')}, Topic: {article.get('topic')}, Title: {article.get('title')[:30]}...", file=sys.stderr)
                    
                    # Add alert task
                    alert_tasks.append(trigger_alert_if_needed(article))
                    # Add save task
                    save_tasks.append(save_processed_article(article, output_file))

                # Run alert checks and save operations concurrently
                print(f"Saving {len(save_tasks)} articles to {output_file}...", file=sys.stderr)
                await asyncio.gather(*alert_tasks, *save_tasks) # Run both sets of tasks
                print("Finished alert checks and saving for this cycle.", file=sys.stderr)

            else:
                print("No articles remaining after filtering. Nothing to process.", file=sys.stderr)

        except Exception as e:
            print(f"An error occurred in the main agent loop: {e}", file=sys.stderr)
            # Avoid crashing the loop, continue to next iteration after sleep

        # Calculate elapsed time and sleep
        elapsed_time = time.monotonic() - start_time
        sleep_time = max(0, FETCH_INTERVAL_SECONDS - elapsed_time)
        print(f"Cycle took {elapsed_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds.", file=sys.stderr)
        await asyncio.sleep(sleep_time)

# Renamed original main to main_agent_loop and updated the entry point
async def main():
    await main_agent_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent interrupted by user. Exiting.")
    except Exception as e:
        logger.exception("Unhandled exception in main execution block.") 
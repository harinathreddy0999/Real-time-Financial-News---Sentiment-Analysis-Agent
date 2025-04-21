# Integration tests for the main agent flow
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, call # Use AsyncMock for async functions

# Make sure src is importable
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the loop and functions to be tested/mocked
from src.main import main_agent_loop, process_single_article, trigger_alert_if_needed, save_processed_article
from src.data_processor import filter_articles # Need this for the test

# Sample data for mock responses
MOCK_RAW_ARTICLE_POSITIVE = {
    "symbol": "TESTP", "title": "Good News Inc.", "description": "Profits soar unexpectedly.",
    "url": "http://test.com/pos", "published_at": "2024-01-01T12:00:00Z", "source": "TestFeed"
}
MOCK_RAW_ARTICLE_NEGATIVE = {
    "symbol": "TESTN", "title": "Bad News Corp.", "description": "Major setback reported.",
    "url": "http://test.com/neg", "published_at": "2024-01-01T12:01:00Z", "source": "TestFeed"
}
MOCK_RAW_ARTICLE_NEUTRAL = {
    "symbol": "TESTU", "title": "Neutral News Ltd.", "description": "Company holds annual meeting.",
    "url": "http://test.com/neu", "published_at": "2024-01-01T12:02:00Z", "source": "TestFeed"
}
MOCK_RAW_ARTICLE_INVALID = {"symbol": "TESTI", "title": "", "description": None, "url": "http://test.com/inv"}

@pytest.mark.asyncio # Mark test as async
async def test_main_loop_single_iteration():
    """Test one full iteration of the main agent loop with mocked external services."""
    # --- Mock Configuration --- 
    # Use nested patches or a single patch with multiple targets if preferred
    with patch('src.main.get_watchlist', return_value=["TESTP", "TESTN", "TESTU"]) as mock_get_watchlist, \
         patch('src.main.get_llm_service_instance') as mock_get_llm_service, \
         patch('src.main.fetch_news_for_watchlist', new_callable=AsyncMock) as mock_fetch, \
         patch('src.main.filter_articles', side_effect=filter_articles) as mock_filter, \
         patch('src.main.summarize_text', new_callable=AsyncMock) as mock_summarize, \
         patch('src.main.analyze_sentiment', new_callable=AsyncMock) as mock_sentiment, \
         patch('src.main.extract_topic', new_callable=AsyncMock) as mock_topic, \
         patch('src.main.asyncio.sleep', new_callable=AsyncMock) as mock_sleep, \
         patch('src.main.send_slack_alert', return_value=True) as mock_send_alert, \
         patch('src.main.save_processed_article', new_callable=AsyncMock) as mock_save_article:

        # Configure mock return values
        mock_fetch.return_value = [
            MOCK_RAW_ARTICLE_POSITIVE,
            MOCK_RAW_ARTICLE_NEGATIVE,
            MOCK_RAW_ARTICLE_NEUTRAL,
            MOCK_RAW_ARTICLE_INVALID # This should be filtered out
        ]
        # Simulate LLM responses based on content
        async def fake_summarize(text):
            if "Good News" in text: return "Summary: Good results"
            if "Bad News" in text: return "Summary: Bad results"
            return "Summary: Neutral event"
        mock_summarize.side_effect = fake_summarize

        async def fake_sentiment(text):
            if "Good News" in text: return "Positive"
            if "Bad News" in text: return "Negative"
            return "Neutral"
        mock_sentiment.side_effect = fake_sentiment

        async def fake_topic(text):
            if "Good News" in text: return "Earnings Beat"
            if "Bad News" in text: return "Guidance Cut"
            return "Meeting"
        mock_topic.side_effect = fake_topic

        # Mock the LLM client availability check
        mock_llm_instance = AsyncMock()
        mock_llm_instance.client = True # Indicate client is available
        mock_get_llm_service.return_value = mock_llm_instance

        # --- Run the Loop (modified to run only once) --- 
        # Create a temporary test loop function that runs the core logic once
        async def run_one_cycle():
            # These would normally come from main_agent_loop scope, pass or mock them
            output_file = "test_output.jsonl" # Dummy path for test
            # Fetch and filter
            raw_articles = await mock_fetch()
            filtered_articles = mock_filter(raw_articles)
            # Process
            processed_articles = []
            if filtered_articles:
                 # Use the actual process_single_article which internally calls mocked LLM funcs
                 tasks = [process_single_article(article) for article in filtered_articles]
                 processed_articles = await asyncio.gather(*tasks)
            # Alert and Save
            alert_tasks = []
            save_tasks = []
            for article in processed_articles:
                # Use actual trigger/save funcs which internally call mocked send/save
                alert_tasks.append(trigger_alert_if_needed(article))
                save_tasks.append(save_processed_article(article, output_file))
            await asyncio.gather(*alert_tasks, *save_tasks)
            return processed_articles # Return processed for assertions

        processed = await run_one_cycle()

        # --- Assertions --- 
        mock_get_watchlist.assert_called_once()
        mock_get_llm_service.assert_called() # Called multiple times indirectly
        mock_fetch.assert_awaited_once()
        mock_filter.assert_called_once_with([
            MOCK_RAW_ARTICLE_POSITIVE,
            MOCK_RAW_ARTICLE_NEGATIVE,
            MOCK_RAW_ARTICLE_NEUTRAL,
            MOCK_RAW_ARTICLE_INVALID
        ])
        assert mock_summarize.await_count == 3
        assert mock_sentiment.await_count == 3
        assert mock_topic.await_count == 3
        assert mock_send_alert.call_count == 2
        assert mock_save_article.await_count == 3

        positive_processed = next(p for p in processed if p['url'] == MOCK_RAW_ARTICLE_POSITIVE['url'])
        negative_processed = next(p for p in processed if p['url'] == MOCK_RAW_ARTICLE_NEGATIVE['url'])
        neutral_processed = next(p for p in processed if p['url'] == MOCK_RAW_ARTICLE_NEUTRAL['url'])

        mock_save_article.assert_any_await(positive_processed, "test_output.jsonl")
        mock_save_article.assert_any_await(negative_processed, "test_output.jsonl")
        mock_save_article.assert_any_await(neutral_processed, "test_output.jsonl")

        assert len(processed) == 3
        assert positive_processed.get('sentiment') == "Positive"
        assert positive_processed.get('summary') == "Summary: Good results"
        assert positive_processed.get('topic') == "Earnings Beat"
        assert negative_processed.get('sentiment') == "Negative"
        assert neutral_processed.get('sentiment') == "Neutral" 
# Tests for src/data_processor.py
import pytest

# Make sure src is importable
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processor import filter_articles

# Sample data for tests
ARTICLE_VALID_1 = {"symbol": "AAPL", "title": "Apple Event", "description": "New iPhones announced.", "url": "http://a.com/1"}
ARTICLE_VALID_2 = {"symbol": "MSFT", "title": "MSFT Results", "description": "Earnings beat expectations.", "url": "http://m.com/1"}
ARTICLE_MISSING_TITLE = {"symbol": "GOOG", "title": None, "description": "Search update.", "url": "http://g.com/1"}
ARTICLE_MISSING_DESC = {"symbol": "TSLA", "title": "Tesla Deliveries", "description": None, "url": "http://t.com/1"}
ARTICLE_EMPTY_TITLE = {"symbol": "AMZN", "title": "", "description": "Prime Day dates.", "url": "http://am.com/1"}
ARTICLE_EMPTY_DESC = {"symbol": "NVDA", "title": "Nvidia Chip", "description": "", "url": "http://n.com/1"}
ARTICLE_DUPLICATE_URL = {"symbol": "AAPL", "title": "Apple Event Again", "description": "Repeated news.", "url": "http://a.com/1"} # Same URL as ARTICLE_VALID_1
ARTICLE_MISSING_URL = {"symbol": "META", "title": "Meta News", "description": "Social media updates.", "url": None}
ARTICLE_EMPTY_URL = {"symbol": "UBER", "title": "Uber Ride", "description": "Ride sharing info.", "url": ""}

@pytest.fixture(autouse=True)
def setup_logging(mocker):
    """Mock logger to prevent log file creation during tests."""
    mocker.patch('src.data_processor.logger')

def test_filter_articles_no_filtering():
    """Test with only valid articles, none should be filtered."""
    articles = [ARTICLE_VALID_1, ARTICLE_VALID_2]
    filtered = filter_articles(articles)
    assert len(filtered) == 2
    # Check if original objects are preserved (identity check)
    assert filtered[0] is ARTICLE_VALID_1
    assert filtered[1] is ARTICLE_VALID_2

def test_filter_articles_missing_content():
    """Test filtering articles with missing or empty title/description."""
    articles = [
        ARTICLE_VALID_1,
        ARTICLE_MISSING_TITLE,
        ARTICLE_VALID_2,
        ARTICLE_MISSING_DESC,
        ARTICLE_EMPTY_TITLE,
        ARTICLE_EMPTY_DESC
    ]
    filtered = filter_articles(articles)
    assert len(filtered) == 2
    assert ARTICLE_VALID_1 in filtered
    assert ARTICLE_VALID_2 in filtered
    assert ARTICLE_MISSING_TITLE not in filtered
    assert ARTICLE_MISSING_DESC not in filtered
    assert ARTICLE_EMPTY_TITLE not in filtered
    assert ARTICLE_EMPTY_DESC not in filtered

def test_filter_articles_duplicate_urls():
    """Test filtering articles with duplicate URLs."""
    articles = [ARTICLE_VALID_1, ARTICLE_VALID_2, ARTICLE_DUPLICATE_URL]
    filtered = filter_articles(articles)
    assert len(filtered) == 2
    assert ARTICLE_VALID_1 in filtered
    assert ARTICLE_VALID_2 in filtered
    # The duplicate URL article should be removed
    assert ARTICLE_DUPLICATE_URL not in filtered

def test_filter_articles_missing_or_empty_urls():
    """Test filtering handles articles with missing or empty URLs (should not filter based on this)."""
    articles = [ARTICLE_VALID_1, ARTICLE_MISSING_URL, ARTICLE_EMPTY_URL, ARTICLE_VALID_2]
    filtered = filter_articles(articles)
    assert len(filtered) == 4 # None should be filtered based on URL validity alone
    assert ARTICLE_VALID_1 in filtered
    assert ARTICLE_MISSING_URL in filtered
    assert ARTICLE_EMPTY_URL in filtered
    assert ARTICLE_VALID_2 in filtered

def test_filter_articles_mixed():
    """Test with a mix of valid, invalid content, and duplicate URLs."""
    articles = [
        ARTICLE_VALID_1,
        ARTICLE_MISSING_TITLE,
        ARTICLE_VALID_2,
        ARTICLE_DUPLICATE_URL, # Duplicate of VALID_1
        ARTICLE_EMPTY_DESC,
        ARTICLE_MISSING_URL # Valid content, just missing URL
    ]
    filtered = filter_articles(articles)
    assert len(filtered) == 3 # VALID_1, VALID_2, MISSING_URL should remain
    assert ARTICLE_VALID_1 in filtered
    assert ARTICLE_VALID_2 in filtered
    assert ARTICLE_MISSING_URL in filtered
    assert ARTICLE_MISSING_TITLE not in filtered
    assert ARTICLE_DUPLICATE_URL not in filtered
    assert ARTICLE_EMPTY_DESC not in filtered

def test_filter_articles_empty_input():
    """Test filtering with an empty input list."""
    articles = []
    filtered = filter_articles(articles)
    assert len(filtered) == 0
    assert filtered == [] 
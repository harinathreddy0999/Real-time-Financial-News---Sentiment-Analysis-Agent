# Tests for src/watchlist.py
import pytest
from unittest.mock import patch

# Make sure src is importable
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.watchlist import get_watchlist

@pytest.fixture(autouse=True)
def setup_logging(mocker):
    """Mock logger to prevent log file creation during tests."""
    mocker.patch('src.watchlist.logger')
    # If get_watchlist directly used config_loader's logger, mock that too
    mocker.patch('src.config_loader.logging')

# Test case 1: Watchlist is present and loaded correctly
@patch('src.watchlist.get_config')
def test_get_watchlist_success(mock_get_config):
    """Test get_watchlist when config returns a valid list."""
    mock_config_data = {"watchlist_symbols": ["AAPL", "GOOG", "$BTC"]}
    mock_get_config.return_value = mock_config_data

    watchlist = get_watchlist()

    assert watchlist == ["AAPL", "GOOG", "$BTC"]
    mock_get_config.assert_called_once()

# Test case 2: Watchlist key is missing in config
@patch('src.watchlist.get_config')
def test_get_watchlist_missing_key(mock_get_config):
    """Test get_watchlist when watchlist_symbols key is missing."""
    mock_config_data = {"some_other_key": "value"} # Missing 'watchlist_symbols'
    mock_get_config.return_value = mock_config_data

    watchlist = get_watchlist()

    assert watchlist == [] # Should return empty list as default
    mock_get_config.assert_called_once()

# Test case 3: Watchlist is present but empty list in config
@patch('src.watchlist.get_config')
def test_get_watchlist_empty_list(mock_get_config):
    """Test get_watchlist when config returns an empty list."""
    mock_config_data = {"watchlist_symbols": []}
    mock_get_config.return_value = mock_config_data

    watchlist = get_watchlist()

    assert watchlist == []
    mock_get_config.assert_called_once()

# Test case 4: Config returns None or empty dict (edge case)
@patch('src.watchlist.get_config')
def test_get_watchlist_empty_config(mock_get_config):
    """Test get_watchlist when get_config returns None or empty dict."""
    # Scenario A: Config is None
    mock_get_config.return_value = None
    watchlist_none = get_watchlist()
    assert watchlist_none == [] # Should handle gracefully

    # Reset mock for Scenario B
    mock_get_config.reset_mock()

    # Scenario B: Config is empty dict
    mock_get_config.return_value = {}
    watchlist_empty = get_watchlist()
    assert watchlist_empty == [] # Should handle gracefully 
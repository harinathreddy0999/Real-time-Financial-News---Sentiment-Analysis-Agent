import os
from dotenv import load_dotenv
import logging

# Determine the path to the .env file (assuming it's in the config/ directory
# relative to the project root, and this script is in src/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(project_root, 'config')
dotenv_path = os.path.join(config_dir, '.env')

# Load environment variables from .env file
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logging.debug(f"Loaded environment variables from {dotenv_path}")
else:
    logging.warning(f".env file not found at {dotenv_path}. Using environment variables or defaults.")

# --- Access Configuration Variables --- #
# You can access variables directly using os.getenv()
# Example:
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# WATCHLIST_SYMBOLS = os.getenv("WATCHLIST_SYMBOLS", "AAPL,GOOG").split(',')

# Or, define a function/class to load and provide settings
def get_config():
    """Loads and returns configuration settings."""
    config = {
        # News API
        "news_api_key": os.getenv("NEWS_API_KEY"),
        # Social Media API
        "social_media_api_key": os.getenv("SOCIAL_MEDIA_API_KEY"),
        "social_media_api_secret": os.getenv("SOCIAL_MEDIA_API_SECRET"),
        "social_media_access_token": os.getenv("SOCIAL_MEDIA_ACCESS_TOKEN"),
        "social_media_access_token_secret": os.getenv("SOCIAL_MEDIA_ACCESS_TOKEN_SECRET"),
        "social_media_bearer_token": os.getenv("SOCIAL_MEDIA_BEARER_TOKEN"),
        # LLM
        "llm_api_key": os.getenv("LLM_API_KEY"),
        "llm_model_name": os.getenv("LLM_MODEL_NAME", "default_model"), # Provide a default
        # Watchlist
        "watchlist_symbols": [s.strip() for s in os.getenv("WATCHLIST_SYMBOLS", "").split(',') if s.strip()],
        # Alerting
        "slack_webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
        # Other
        "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
    }
    return config

# Example usage (optional, for testing the loader)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    settings = get_config()
    logging.info("Loaded configuration:")
    # Avoid printing sensitive keys directly in production logs
    safe_settings = {k: (v[:4] + '...' if k.endswith('_key') and v else v) for k, v in settings.items()}
    logging.info(safe_settings) 
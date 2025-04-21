from src.config_loader import get_config
from src.logger_setup import get_logger

logger = get_logger(__name__)

def get_watchlist() -> list[str]:
    """Retrieves the watchlist symbols from the configuration."""
    config = get_config()
    watchlist = config.get("watchlist_symbols", [])
    if not watchlist:
        logger.warning("Watchlist is empty. Check your configuration (WATCHLIST_SYMBOLS in .env).")
    else:
        logger.info(f"Loaded watchlist: {watchlist}")
    return watchlist

# Example usage (optional)
if __name__ == "__main__":
    from src.logger_setup import setup_logging
    setup_logging() # Initialize logging for standalone run
    watchlist = get_watchlist()
    if watchlist:
        logger.info(f"Retrieved watchlist: {watchlist}")
    else:
        logger.error("Failed to retrieve watchlist or it is empty.") 
from slack_sdk.webhook import WebhookClient
from typing import Optional, Dict, Any, List

from src.config_loader import get_config
from src.logger_setup import get_logger

logger = get_logger(__name__)

# Global variable to hold the webhook client instance
_webhook_client: Optional[WebhookClient] = None

def _initialize_webhook_client() -> Optional[WebhookClient]:
    """Initializes the Slack Webhook client using the URL from config."""
    global _webhook_client
    if _webhook_client is not None:
        return _webhook_client

    config = get_config()
    webhook_url = config.get("slack_webhook_url")

    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not found in configuration. Slack alerts will be disabled.")
        return None

    try:
        _webhook_client = WebhookClient(webhook_url)
        logger.info("Slack Webhook client initialized successfully.")
        return _webhook_client
    except Exception as e:
        logger.exception(f"Failed to initialize Slack Webhook client: {e}")
        return None

def send_slack_alert(text: str, blocks: Optional[List[Dict[str, Any]]] = None) -> bool:
    """Sends an alert message to the configured Slack channel.

    Args:
        text: The fallback text message.
        blocks: Optional Slack Block Kit elements for richer formatting.

    Returns:
        True if the alert was sent successfully, False otherwise.
    """
    client = _initialize_webhook_client()
    if not client:
        logger.debug(f"Slack client not available. Alert not sent: {text[:100]}...")
        return False

    try:
        response = client.send(text=text, blocks=blocks)
        if response.status_code == 200:
            logger.info(f"Slack alert sent successfully.")
            logger.debug(f"Slack alert content: {text[:100]}...")
            return True
        else:
            logger.error(f"Failed to send Slack alert. Status: {response.status_code}, Body: {response.body}")
            return False
    except Exception as e:
        logger.exception(f"Error sending Slack alert: {e}")
        return False

# Example usage (optional)
if __name__ == "__main__":
    from src.logger_setup import setup_logging
    import asyncio # Need asyncio to run async functions if added later
    setup_logging()

    # Ensure SLACK_WEBHOOK_URL is set in config/.env
    logger.info("--- Testing Slack Alerting Service --- ")

    # Test 1: Simple text message
    success_text = send_slack_alert("This is a test alert from the Financial News Agent.")
    logger.info(f"Simple text alert success: {success_text}")

    # Test 2: Using Block Kit for formatting
    test_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Financial Agent Test Alert :tada:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "*Type:*\nTest"},
                {"type": "mrkdwn", "text": "*Severity:*\nInfo"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "This alert confirms that the *Slack integration* is working correctly using Block Kit."
            }
        }
    ]
    success_block = send_slack_alert(text="Fallback text for Block Kit test", blocks=test_blocks)
    logger.info(f"Block Kit alert success: {success_block}")

    logger.info("--- Finished Slack Alerting Service Test --- ") 
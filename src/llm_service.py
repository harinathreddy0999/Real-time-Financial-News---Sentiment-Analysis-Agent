import os
from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.exceptions import OutputParserException

from src.config_loader import get_config
from src.logger_setup import get_logger

logger = get_logger(__name__)

class LLMService:
    def __init__(self):
        self.client = self._initialize_client()

    def _initialize_client(self) -> Optional[ChatGoogleGenerativeAI]:
        """Initializes and returns the LLM client."""
        config = get_config()
        api_key = config.get("llm_api_key")
        
        # Use a specific valid model name by default (Gemini 1.5 Pro is widely available)
        DEFAULT_MODEL = "gemini-1.5-pro"
        model_name = config.get("llm_model_name")
        
        # If model name isn't specified in config, use the default
        if not model_name:
            model_name = DEFAULT_MODEL
            logger.info(f"No LLM_MODEL_NAME specified in config, using default: {DEFAULT_MODEL}")

        if not api_key:
            logger.error("LLM_API_KEY not found in configuration. LLMService cannot function.")
            return None
        
        # Add debug logging with masked API key
        key_preview = api_key[:4] + "..." if api_key and len(api_key) > 4 else "None"
        logger.info(f"Initializing Gemini LLM client with key starting with: {key_preview}")
        logger.info(f"Using model: {model_name}")

        try:
            # You might need to adjust parameters based on the specific Gemini model
            # and desired behavior (temperature, top_p, etc.)
            client = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.2, # Lower temperature for more deterministic results
                # convert_system_message_to_human=True # May be needed depending on model/task
            )
            logger.info(f"Successfully initialized Gemini LLM client with model: {model_name}")
            
            # Test connection with a simple prompt
            logger.info("Testing LLM connection with a simple prompt...")
            try:
                test_response = client.invoke("Hello, are you working?")
                logger.info(f"LLM test successful. Response: {test_response.content[:100]}...")
            except Exception as test_e:
                logger.error(f"LLM test failed with error: {test_e}")
                
            return client
        except Exception as e:
            logger.exception(f"Failed to initialize Gemini LLM client: {e}")
            return None

    def generate_response(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Generates a response from the LLM given system and user prompts."""
        if not self.client:
            logger.error("LLM client not initialized. Cannot generate response.")
            return None

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            # Limit prompt logging length
            log_user_prompt = (user_prompt[:200] + '...') if len(user_prompt) > 200 else user_prompt
            logger.debug(f"Sending request to LLM. System: '{system_prompt}', User: '{log_user_prompt}'")
            response = self.client.invoke(messages)
            # Limit response logging length
            log_response_content = (response.content[:200] + '...') if len(response.content) > 200 else response.content
            logger.debug(f"Received response from LLM: {log_response_content}")
            return response.content
        except OutputParserException as e:
            logger.error(f"Error parsing LLM output: {e}")
            return None
        except Exception as e:
            # Catch potential API errors (rate limits, auth issues, etc.)
            logger.exception(f"Error during LLM invocation: {e}")
            return None

# --- Placeholder functions for specific tasks --- #
# These will be implemented in the next steps using the LLMService

def get_llm_service_instance() -> LLMService:
    """Returns a singleton instance of the LLMService."""
    # Basic singleton pattern
    if not hasattr(get_llm_service_instance, "_instance"):
        get_llm_service_instance._instance = LLMService()
    return get_llm_service_instance._instance

# Updated Summarization Function
async def summarize_text(text: str) -> Optional[str]:
    """Summarizes the given text using the LLM."""
    llm_service = get_llm_service_instance()
    if not llm_service or not llm_service.client:
        logger.error("LLM service not available for summarization.")
        return None

    # Define the prompt for summarization
    # Keep it focused on extracting key financial information concisely
    system_prompt = "You are an expert financial analyst assistant. Summarize the key financial information or event described in the following text in one or two concise sentences. Focus on the core news relevant to an investor."
    user_prompt = f"Text to summarize:\n\n```\n{text}\n```\n\nConcise financial summary:"

    summary = llm_service.generate_response(system_prompt, user_prompt)

    if summary:
        logger.debug(f"Generated summary: {summary}")
    else:
        logger.warning(f"Failed to generate summary for text: {text[:100]}...")

    return summary

# Updated Sentiment Analysis Function
async def analyze_sentiment(text: str) -> Optional[str]:
    """Analyzes the sentiment of the given text using the LLM, returning Positive, Negative, or Neutral."""
    llm_service = get_llm_service_instance()
    if not llm_service or not llm_service.client:
        logger.error("LLM service not available for sentiment analysis.")
        return None

    # Define the prompt for financial sentiment analysis
    system_prompt = (
        "You are an expert financial analyst specializing in sentiment analysis. "
        "Analyze the sentiment of the following financial text (e.g., news headline, description, social media post). "
        "Consider the potential impact on the stock or market mentioned. "
        "Respond with only ONE of the following words: Positive, Negative, or Neutral."
    )
    user_prompt = f"Financial text:\n\n```\n{text}\n```\n\nSentiment (Positive/Negative/Neutral):"

    sentiment = llm_service.generate_response(system_prompt, user_prompt)

    # Validate and clean the output
    if sentiment:
        sentiment = sentiment.strip().capitalize()
        if sentiment in ["Positive", "Negative", "Neutral"]:
            logger.debug(f"Generated sentiment: {sentiment}")
            return sentiment
        else:
            logger.warning(f"LLM returned unexpected sentiment value: '{sentiment}' for text: {text[:100]}... Attempting fallback or returning None.")
            # Optional: Could try a follow-up prompt asking for re-classification
            return None # Or return the raw value if preferred, but it might break downstream logic
    else:
        logger.warning(f"Failed to generate sentiment for text: {text[:100]}...")
        return None

# Updated Topic Extraction Function
async def extract_topic(text: str) -> Optional[str]:
    """Extracts the main financial topic or event from the given text using the LLM."""
    llm_service = get_llm_service_instance()
    if not llm_service or not llm_service.client:
        logger.error("LLM service not available for topic extraction.")
        return None

    # Define the prompt for financial topic extraction
    system_prompt = (
        "You are an expert financial analyst. Read the following financial text and identify the main topic or event being discussed. "
        "Be specific and concise. Examples: 'Earnings Report', 'Product Launch', 'Executive Appointment', 'Stock Split', 'Macroeconomic Data Release', 'Regulatory Filing', 'Merger/Acquisition'."
        "Respond with only the topic name."
    )
    user_prompt = f"Financial text:\n\n```\n{text}\n```\n\nMain Financial Topic/Event:"

    topic = llm_service.generate_response(system_prompt, user_prompt)

    if topic:
        topic = topic.strip()
        logger.debug(f"Extracted topic: {topic}")
        return topic
    else:
        logger.warning(f"Failed to extract topic for text: {text[:100]}...")
        return None


# Example usage (optional)
if __name__ == "__main__":
    from src.logger_setup import setup_logging
    import asyncio # Add asyncio import for async example
    setup_logging() # Initialize logging for standalone run

    # Ensure LLM_API_KEY is set in config/.env
    service = get_llm_service_instance()

    async def run_llm_tests(): # Wrap tests in async function
        if service.client:
            logger.info("--- Running LLM Service Standalone Test --- ")
            test_system_prompt = "You are a helpful assistant."
            test_user_prompt = "Explain the concept of asynchronous programming in Python in one sentence."
            response = service.generate_response(test_system_prompt, test_user_prompt)
            if response:
                logger.info(f"Test Query: {test_user_prompt}")
                logger.info(f"LLM Response: {response}")
            else:
                logger.error("Failed to get response from LLM for basic test.")

            # Test Summarization
            logger.info("--- Testing Summarization --- ")
            sample_news = "Quantum Computing Inc. announced today that its board of directors has approved a 1-for-50 reverse stock split of its common stock, effective May 10, 2024. The stock symbol will remain QUBT."
            summary = await summarize_text(sample_news)
            if summary:
                logger.info(f"Original Text: {sample_news}")
                logger.info(f"Generated Summary: {summary}")
            else:
                logger.error("Failed to generate summary.")

            # Test Sentiment Analysis
            logger.info("--- Testing Sentiment Analysis --- ")
            positive_news = "Apple reported record profits for Q2, beating analyst expectations on strong iPhone sales."
            negative_news = "Regulators fined ACME Corp $1B for environmental violations, stock price plummets."
            neutral_news = "The next FOMC meeting is scheduled for Tuesday, market participants await the outcome."

            for news in [positive_news, negative_news, neutral_news]:
                sentiment = await analyze_sentiment(news)
                if sentiment:
                    logger.info(f"Text: {news}")
                    logger.info(f"Generated Sentiment: {sentiment}")
                else:
                    logger.error(f"Failed to generate sentiment for: {news}")

            # Test Topic Extraction
            logger.info("--- Testing Topic Extraction --- ")
            topic_examples = [
                "Quantum Computing Inc. announced a 1-for-50 reverse stock split.",
                "Apple reported record profits for Q2, beating analyst expectations.",
                "Microsoft revealed its new Surface Pro 10 lineup today.",
                "The Federal Reserve hinted at potential rate cuts later this year."
            ]
            for text in topic_examples:
                topic = await extract_topic(text)
                if topic:
                    logger.info(f"Text: {text}")
                    logger.info(f"Extracted Topic: {topic}")
                else:
                    logger.error(f"Failed to extract topic for: {text}")

            logger.info("--- Finished LLM Service Standalone Tests --- ")
        else:
            logger.error("LLM Service client could not be initialized. Check API key and logs.")

    # Run the async tests
    asyncio.run(run_llm_tests()) 
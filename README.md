# Real-time Financial News & Sentiment Analysis Agent

## Overview

This application continuously collects, analyzes, and monitors financial news for user-specified companies and assets. It uses AI to extract relevant insights, sentiment, and potential market impacts, delivering them through an interactive dashboard and automated alerts.

## Features

### 1. Automated News Collection
- **Real-time Monitoring**: Continuously scans financial news sources for updates on your watchlist
- **Configurable Watchlist**: Track specific companies, stocks, cryptocurrencies, and market sectors
- **Multi-source Aggregation**: Collects news from various reputable financial news providers

### 2. AI-Powered Analysis
- **Sentiment Analysis**: Classifies news as positive, negative, or neutral
- **Key Information Extraction**: Identifies critical facts, figures, and trends
- **Topic Classification**: Categorizes news by topic (earnings, product launches, regulatory, etc.)
- **Impact Assessment**: Estimates potential market impact and relevance

### 3. Intelligent Alerting
- **Sentiment-based Alerts**: Get notified of significant positive or negative news
- **Priority Ranking**: Alerts are ranked by potential impact and relevance
- **Configurable Thresholds**: Set your own criteria for what triggers an alert
- **Slack Integration**: Receive alerts via Slack (configurable)

### 4. Interactive Dashboard
- **Real-time Updates**: Dashboard refreshes automatically to show the latest news
- **Filtering and Sorting**: Filter by company, sentiment, date, and topic
- **Sentiment Visualization**: Charts showing sentiment distribution across your watchlist
- **Detailed Analysis**: View AI-generated summaries and key takeaways for each article
- **Source Links**: Direct links to original news sources

## How It Works

### Architecture & Data Flow

1. **Backend Agent (src/main.py)**:
   - Runs in the background on a configurable schedule (default: every 15 minutes)
   - Fetches latest news for all symbols in your watchlist
   - Sends each article for processing by the LLM (AI) service
   - Saves processed articles to persistent storage
   - Triggers alerts for significant news

2. **LLM Service (src/llm_service.py)**:
   - Processes each article using Google's Gemini API
   - Extracts key information and performs sentiment analysis
   - Generates concise summaries optimized for financial context
   - Determines alert worthiness based on content and sentiment

3. **News Fetcher (src/news_fetcher.py)**:
   - Connects to NewsAPI to retrieve relevant financial news
   - Performs initial filtering and deduplication
   - Handles rate limiting and API quotas

4. **Streamlit Dashboard (src/streamlit_app.py)**:
   - Provides the user interface for interacting with processed news
   - Visualizes sentiment data and article distribution
   - Enables filtering and exploration of news articles
   - Auto-refreshes to display latest content

### Processing Pipeline:

```
News Sources → News Fetcher → Backend Agent → LLM Processing → 
Sentiment Analysis → Storage → Dashboard Display & Alerts
```

## Technical Stack

### Core Technologies
- **Python 3.10+**: Primary programming language
- **Streamlit**: Interactive web dashboard framework
- **Google Gemini Pro**: LLM for natural language processing and analysis
- **NewsAPI**: Primary data source for financial news articles

### Key Libraries & Dependencies
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualizations
- **httpx**: Asynchronous HTTP client for API calls
- **python-dotenv**: Environment variable management
- **logging**: Structured logging and diagnostics
- **jsonlines**: Efficient storage of processed articles
- **asyncio**: Asynchronous I/O operations

### Infrastructure
- **Local Development**: Runs completely on local machine
- **Virtual Environment**: Python venv for dependency isolation
- **File-based Storage**: JSONL format for processed articles
- **Configuration**: Environment variables via .env file
- **Scheduling**: Internal Python-based scheduling system

### API Integrations
- **NewsAPI**: Financial news retrieval
- **Google Gemini API**: AI-powered text analysis
- **Slack Webhooks API**: Optional alert notifications

## Getting Started

### Prerequisites
- Python 3.10 or higher
- API keys for:
  - NewsAPI (required)
  - Google Gemini API (required)
  - Slack Webhook URL (optional)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/financial-news-agent.git
cd financial-news-agent
```

2. **Set up Python environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure API keys**:
   - Copy `config/.env.example` to `config/.env`
   - Add your API keys to the `.env` file

4. **Run the application**:
```bash
# Run both backend agent and frontend dashboard
python run_app.py

# Or run components separately:
# Backend only
python -m src.main

# Frontend only
streamlit run src/streamlit_app.py
```

5. **Access the dashboard**:
   - Open your browser to http://localhost:8501

### Configuration Options

You can customize the application by modifying the following settings in `config/.env`:

- `WATCHLIST_SYMBOLS`: Comma-separated list of companies/assets to track
- `NEWS_API_KEY`: Your NewsAPI key
- `LLM_API_KEY`: Your Google Gemini API key
- `LLM_MODEL_NAME`: Gemini model to use (default: "gemini-1.5-pro")
- `NEWS_FETCH_INTERVAL`: How often to fetch news (in seconds)
- `SLACK_WEBHOOK_URL`: URL for Slack notifications (optional)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, etc.)

## Usage Examples

### Basic Dashboard Navigation
1. View the latest news articles in the main panel
2. Filter by symbol or sentiment using the dropdown menus
3. Click "Read Full Article" to view the original source
4. See sentiment distribution in the charts

### Working with Alerts
1. Alerts appear in the right sidebar
2. Critical alerts are sent to Slack if configured
3. Alerts are generated for significant positive or negative news

### Custom Configuration
1. Edit your watchlist in `config/.env`
2. Restart the application to apply changes
3. Adjust the refresh interval in the dashboard settings

## Development and Extending

The modular architecture makes it easy to extend the application:

- Add new data sources in the `news_fetcher.py` module
- Modify the LLM prompts in `llm_service.py` to extract different information
- Enhance the dashboard by adding new visualizations to `streamlit_app.py`
- Implement additional notification channels beyond Slack

## Limitations

- NewsAPI free tier has a limited number of requests per day
- LLM processing can take a few seconds per article
- The application requires an internet connection for API access
- Large volumes of news may require additional storage management

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- NewsAPI for providing financial news data
- Google Gemini for AI-powered text analysis
- Streamlit for the interactive dashboard framework 
# Technical Stack: Real-time Financial News & Sentiment Analysis Agent

## Core Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.10+ | Primary programming language |
| Frontend | Streamlit | 1.30+ | Interactive web dashboard |
| AI/LLM | Google Gemini | 1.5 Pro | Natural language processing |
| Data Source | NewsAPI | v2 | Financial news retrieval |
| Data Storage | JSONL | - | Efficient semi-structured data storage |
| Visualization | Plotly | 6.0+ | Interactive data visualization |
| HTTP Client | httpx | 0.25+ | Asynchronous API requests |
| Configuration | python-dotenv | 1.0+ | Environment variable management |

## Architecture Details

### System Components

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  News Sources   │───>│  News Fetcher   │───>│  Backend Agent  │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Dashboard    │<───│   Data Store    │<───│  LLM Processor  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Modules

1. **Backend Agent (`src/main.py`)**
   - **Language:** Python
   - **Framework:** asyncio for concurrent operations
   - **Dependencies:**
     - `time` for scheduling
     - `logging` for structured logging
     - `os` for file operations
     - `json` for data serialization
   - **Key Functions:**
     - `main_agent_loop()`: Main execution loop
     - `process_single_article()`: Article processing pipeline
     - `save_processed_article()`: Data persistence
     - `trigger_alert_if_needed()`: Alert mechanism

2. **LLM Service (`src/llm_service.py`)**
   - **Language:** Python
   - **AI Model:** Google Gemini 1.5 Pro
   - **Dependencies:**
     - `google.generativeai` for Gemini integration
     - `json` for structured data handling
   - **Key Functions:**
     - `init_llm_client()`: Initialize Gemini client
     - `process_article()`: Process article with LLM
     - `structured_financial_analysis()`: Extract structured insights

3. **News Fetcher (`src/news_fetcher.py`)**
   - **Language:** Python
   - **Data Source:** NewsAPI
   - **Dependencies:**
     - `httpx` for async HTTP requests
     - `datetime` for time-based queries
   - **Key Functions:**
     - `fetch_news_for_symbol()`: Retrieve news for specific symbol
     - `fetch_all_news()`: Aggregate news for watchlist

4. **Streamlit Dashboard (`src/streamlit_app.py`)**
   - **Language:** Python
   - **Framework:** Streamlit
   - **Dependencies:**
     - `streamlit` for web interface
     - `pandas` for data manipulation
     - `plotly` for interactive visualizations
   - **Key Components:**
     - Real-time news display
     - Filtering and search
     - Sentiment visualization
     - System status monitoring

### Data Flow

1. **Collection Phase:**
   - NewsAPI queries based on watchlist symbols
   - Results filtered by relevance and recency
   - Raw articles stored temporarily

2. **Processing Phase:**
   - Articles sent to Gemini LLM for analysis
   - Structured data extraction:
     - Sentiment (Positive/Negative/Neutral)
     - Topic classification
     - Key metrics and impact assessment
     - Concise summary

3. **Storage Phase:**
   - Processed articles saved as JSONL
   - Each record contains:
     - Original article metadata
     - AI-generated analysis
     - Sentiment and classification
     - Processing timestamp

4. **Presentation Phase:**
   - Data loaded into Streamlit dashboard
   - Interactive filtering and visualization
   - Auto-refreshing display

### API Integration Details

1. **NewsAPI**
   - **Endpoint:** `https://newsapi.org/v2/everything`
   - **Authentication:** API Key (header)
   - **Rate Limits:** Varies by plan (free: 100 requests/day)
   - **Query Parameters:**
     - `q`: Search query (company symbol)
     - `language`: en
     - `sortBy`: publishedAt
     - `pageSize`: Number of results

2. **Google Gemini API**
   - **Endpoint:** Google AI Platform
   - **Authentication:** API Key
   - **Model:** gemini-1.5-pro
   - **Parameters:**
     - Structured output format
     - Temperature: 0.2 (more deterministic)
     - Max output tokens: 1024

3. **Slack API (Optional)**
   - **Endpoint:** Custom Webhook URL
   - **Authentication:** Webhook token
   - **Format:** JSON payload
   - **Features:** Formatted message cards

## Development Environment

### Local Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with your API keys

# Run application
python run_app.py
```

### Directory Structure

```
├── config/                 # Configuration
│   ├── .env                # Environment variables
│   └── .env.example        # Template for .env
├── data/                   # Data storage
│   └── processed_news.jsonl # Processed articles
├── logs/                   # Log files
│   └── financial_agent.log
├── src/                    # Source code
│   ├── __init__.py
│   ├── llm_service.py      # LLM integration
│   ├── logger_setup.py     # Logging configuration
│   ├── main.py             # Backend agent
│   ├── news_fetcher.py     # NewsAPI integration
│   └── streamlit_app.py    # Dashboard UI
├── test/                   # Unit tests
│   └── ...
├── venv/                   # Virtual environment
├── .gitignore
├── README.md
├── requirements.txt        # Dependencies
├── run_app.py              # Application entry point
└── test_news_fetch.py      # Test data generator
```

## Performance Characteristics

| Component | Performance Metrics | Optimization |
|-----------|---------------------|-------------|
| News Fetching | ~1-3 seconds per API call | Asynchronous calls, caching |
| LLM Processing | ~2-5 seconds per article | Optimized prompts, parallel processing |
| Dashboard | ~1 second load time | Efficient data loading, pagination |
| Storage | ~100KB per 100 articles | JSONL format (efficient for appending) |

## Security Considerations

- **API Keys:** Stored in .env file (not version controlled)
- **Data Storage:** Local only, no sensitive user data
- **Network Security:** HTTPS for all API calls
- **Dependencies:** Regular updates recommended

## Scalability Potential

The current implementation is designed for personal use but could be extended:

- **Cloud Deployment:** Containerized with Docker
- **Database Integration:** Replace JSONL with PostgreSQL/MongoDB
- **Multi-user Support:** User authentication and data separation
- **Advanced Analytics:** Time series analysis, market correlation
- **Additional Sources:** Integration with more financial data providers

## Technologies Considered but Not Used

| Technology | Purpose | Reason Not Used |
|------------|---------|-----------------|
| Django/Flask | Web Backend | Streamlit sufficient for UI needs |
| OpenAI API | LLM Provider | Google Gemini chosen for cost & capability |
| SQLite | Database | JSONL simpler for current requirements |
| Docker | Containerization | Not needed for local deployment | 
# Real-time Financial News & Sentiment Analysis Agent 📈🤖

> A Python application that continuously monitors financial news for your watchlist, uses **Google Gemini** for AI-powered sentiment analysis and summarization, and presents insights via an interactive **Streamlit** dashboard and optional **Slack** alerts. Stay ahead with curated, analyzed market news!

---

## ✨ Key Features

* **Automated News Aggregation:** Continuously fetches relevant financial news from **NewsAPI** based on a configurable watchlist (stocks, crypto, sectors).
* **AI-Driven Analysis:** Leverages **Google Gemini Pro** to perform:
    * Sentiment classification (Positive/Negative/Neutral).
    * Key topic identification (Earnings, M&A, etc.).
    * Concise summarization of articles.
    * Potential market impact assessment.
* **Interactive Dashboard:** A **Streamlit** interface providing:
    * Real-time feed of analyzed news.
    * Filtering by symbol, sentiment, date.
    * Sentiment visualizations (**Plotly** charts).
    * Direct links to source articles.
* **Intelligent Alerting:** Configurable notifications (via Slack) triggered by significant news events or sentiment shifts.

---

## 🚀 Core Technologies

* **Language:** **Python 3.10+**
* **AI / LLM:** **Google Gemini Pro**
* **Frontend:** **Streamlit**
* **Data Source:** **NewsAPI**
* **Key Libraries:** `httpx` (async HTTP), `Plotly` (charts), `python-dotenv` (config), `asyncio` (concurrency), `jsonlines` (storage)

---

## 🛠️ Getting Started

### Prerequisites

* Python 3.10 or higher
* **NewsAPI Key** (Required)
* **Google Gemini API Key** (Required)
* Slack Webhook URL (Optional, for alerts)

### Quick Installation & Run

1.  **Clone Repository:**
    ```bash
    git clone [https://github.com/yourusername/financial-news-agent.git](https://github.com/yourusername/financial-news-agent.git)
    cd financial-news-agent
    ```
    *(Replace with your actual repository URL)*

2.  **Set Up Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure API Keys & Watchlist:**
    * Copy `config/.env.example` to `config/.env`.
    * Open `config/.env` and enter your **`NEWS_API_KEY`** and **`LLM_API_KEY`** (Gemini Key).
    * Update `WATCHLIST_SYMBOLS` with your desired comma-separated stocks/assets (e.g., `AAPL,TSLA,BTC-USD`).
    * Add `SLACK_WEBHOOK_URL` if using Slack alerts.

4.  **Run the Application:**
    ```bash
    python run_app.py
    ```
    *(This typically runs both the backend agent and the Streamlit dashboard)*

5.  **Access Dashboard:**
    * Open your web browser to `http://localhost:8501`

---

## ⚙️ Configuration

Key parameters like the watchlist, API keys, news fetch frequency, and alert settings can be adjusted in the `config/.env` file.

---

## 🧩 How It Works (High Level)

1.  **News Fetcher** gets latest articles from NewsAPI for the watchlist.
2.  **Backend Agent** orchestrates the flow, sending articles to the LLM Service.
3.  **LLM Service** uses Google Gemini to analyze sentiment, summarize, and classify topics.
4.  Processed data is stored (as `JSONL` files).
5.  **Streamlit Dashboard** reads the stored data to display insights and visualizations.
6.  Significant findings trigger alerts (if configured).

---

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

---

## 🙏 Acknowledgements

* News data provided by **NewsAPI**.
* AI analysis powered by **Google Gemini**.
- Streamlit for the interactive dashboard framework 

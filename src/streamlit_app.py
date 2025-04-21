import streamlit as st
import pandas as pd
import json
import os
import time
import glob
import plotly.express as px
from datetime import datetime, timedelta
import subprocess
import threading
import re
import sys

# Set page title and layout
st.set_page_config(
    page_title="Financial News & Sentiment Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the UI
st.markdown("""
<style>
    .sentiment-positive {
        color: #0ECB81;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: rgba(14, 203, 129, 0.1);
    }
    .sentiment-negative {
        color: #F6465D;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: rgba(246, 70, 93, 0.1);
    }
    .sentiment-neutral {
        color: #808A9D;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: rgba(128, 138, 157, 0.1);
    }
    .card {
        border: 1px solid #e6e9ed;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        background-color: white;
    }
    .topic-tag {
        background-color: #f0f2f5;
        color: #4B587C;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
    }
    .symbol-tag {
        background-color: #e7f5ff;
        color: #0076CE;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .article-title {
        font-size: 1.2em;
        margin-bottom: 10px;
        color: #1E2329;
    }
    .article-summary {
        color: #474D57;
    }
    .article-meta {
        color: #707A8A;
        font-size: 0.8em;
    }
    .article-link {
        color: #0076CE;
        text-decoration: none;
        background-color: #e7f5ff;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.85em;
        display: inline-block;
        font-weight: bold;
        transition: background-color 0.2s;
    }
    .article-link:hover {
        background-color: #d0ebff;
        text-decoration: none;
    }
    .dashboard-title {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 20px;
        color: #1E2329;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .status-active {
        background-color: #0ECB81;
    }
    .status-inactive {
        background-color: #F6465D;
    }
    .status-unknown {
        background-color: #FCD535;
    }
    .backend-status-box {
        background-color: #F8FAFD;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 15px;
    }
    .alert-history {
        height: 200px;
        overflow-y: auto;
        background-color: #F8FAFD;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Constants
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
JSONL_PATH = os.path.join(DATA_DIR, 'processed_news.jsonl')

# Check if backend is running
def is_backend_running():
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        output = result.stdout
        # Look for the main.py process
        return 'src.main' in output or 'src/main.py' in output
    except Exception:
        return False

# Function to check if API keys are configured
def check_api_keys():
    env_path = os.path.join(CONFIG_DIR, '.env')
    if not os.path.exists(env_path):
        return {
            'news_api': {'status': 'unknown', 'message': '.env file not found'},
            'llm_api': {'status': 'unknown', 'message': '.env file not found'},
            'slack_webhook': {'status': 'unknown', 'message': '.env file not found'},
        }
    
    try:
        keys = {}
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        keys[key] = value
        
        result = {}
        
        # Check NEWS_API_KEY
        news_key = keys.get('NEWS_API_KEY', '')
        if news_key and news_key != 'YOUR_NEWS_API_KEY':
            result['news_api'] = {'status': 'active', 'message': 'Configured'}
        else:
            result['news_api'] = {'status': 'inactive', 'message': 'Not configured or invalid'}
        
        # Check LLM_API_KEY
        llm_key = keys.get('LLM_API_KEY', '')
        if llm_key and llm_key != 'YOUR_LLM_API_KEY':
            result['llm_api'] = {'status': 'active', 'message': 'Configured'}
        else:
            result['llm_api'] = {'status': 'inactive', 'message': 'Not configured or invalid'}
        
        # Check SLACK_WEBHOOK_URL
        slack_url = keys.get('SLACK_WEBHOOK_URL', '')
        if slack_url and slack_url != 'YOUR_SLACK_WEBHOOK_URL':
            # Just show if it's configured without revealing URL parts
            result['slack_webhook'] = {'status': 'active', 'message': 'Configured'}
        else:
            result['slack_webhook'] = {'status': 'inactive', 'message': 'Not configured or invalid'}
        
        return result
    except Exception as e:
        return {
            'news_api': {'status': 'unknown', 'message': f'Error checking: {str(e)}'},
            'llm_api': {'status': 'unknown', 'message': f'Error checking: {str(e)}'},
            'slack_webhook': {'status': 'unknown', 'message': f'Error checking: {str(e)}'},
        }

# Get watchlist from config
def get_watchlist_from_config():
    env_path = os.path.join(CONFIG_DIR, '.env')
    if not os.path.exists(env_path):
        return []
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('WATCHLIST_SYMBOLS='):
                    _, value = line.strip().split('=', 1)
                    # Remove quotes if present and split by comma
                    value = value.strip('"\'')
                    return [s.strip() for s in value.split(',') if s.strip()]
        return []
    except Exception:
        return []

def load_data():
    """Load processed news articles from the JSONL file."""
    if not os.path.exists(JSONL_PATH):
        return pd.DataFrame()
    
    # Read the JSONL file line by line
    articles = []
    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                articles.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    if not articles:
        return pd.DataFrame()
    
    # Convert to DataFrame and do some basic processing
    df = pd.DataFrame(articles)
    
    # Process published_at dates if they exist
    if 'published_at' in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        df = df.sort_values('published_at', ascending=False)
    
    return df

def format_datetime(dt):
    """Format datetime for display."""
    if pd.isna(dt):
        return "N/A"
    try:
        dt = pd.to_datetime(dt)
        now = pd.Timestamp.now()
        diff = now - dt
        
        if diff.days >= 1:
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds} seconds ago"
    except:
        return str(dt)

def render_article_card(article):
    """Render a news article as a styled card."""
    sentiment = article.get('sentiment', 'Unknown')
    sentiment_class = f"sentiment-{sentiment.lower()}" if sentiment in ['Positive', 'Negative', 'Neutral'] else ""
    
    symbol = article.get('symbol', 'Unknown')
    title = article.get('title', 'No title available')
    summary = article.get('summary', 'No summary available')
    topic = article.get('topic', 'General')
    url = article.get('url', '#')
    source = article.get('source', 'Unknown source')
    published_at = format_datetime(article.get('published_at'))
    
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
            <div>
                <span class="symbol-tag">{symbol}</span>
                <span class="topic-tag">{topic}</span>
            </div>
            <span class="{sentiment_class}">{sentiment}</span>
        </div>
        <div class="article-title">{title}</div>
        <div class="article-summary">{summary}</div>
        <div class="article-meta" style="margin-top: 10px;">
            <span>{source}</span> • <span>{published_at}</span>
        </div>
        <div style="margin-top: 10px;">
            <a href="{url}" target="_blank" class="article-link">Read Full Article</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recent_alerts(df):
    """Render recent alerts from processed articles."""
    if df.empty:
        return []
    
    # Get articles with positive or negative sentiment
    alerts_df = df[df['sentiment'].isin(['Positive', 'Negative'])].copy()
    if alerts_df.empty:
        return []
        
    # Take most recent 5
    alerts_df = alerts_df.sort_values('published_at', ascending=False).head(5)
    
    alerts = []
    for _, row in alerts_df.iterrows():
        sentiment = row.get('sentiment', '')
        symbol = row.get('symbol', '')
        title = row.get('title', '')
        timestamp = format_datetime(row.get('published_at'))
        
        alert = {
            'sentiment': sentiment,
            'symbol': symbol,
            'title': title,
            'timestamp': timestamp
        }
        alerts.append(alert)
    
    return alerts

def get_processing_stats(df):
    """Calculate processing statistics."""
    stats = {
        'total_articles': 0,
        'total_symbols': 0,
        'newest_article': 'N/A',
        'oldest_article': 'N/A',
        'articles_by_symbol': {},
        'sentiment_counts': {'Positive': 0, 'Negative': 0, 'Neutral': 0},
    }
    
    if df.empty:
        return stats
    
    stats['total_articles'] = len(df)
    stats['total_symbols'] = df['symbol'].nunique()
    
    if 'published_at' in df.columns:
        newest = df['published_at'].max()
        oldest = df['published_at'].min()
        if not pd.isna(newest):
            stats['newest_article'] = format_datetime(newest)
        if not pd.isna(oldest):
            stats['oldest_article'] = format_datetime(oldest)
    
    # Count by symbol
    stats['articles_by_symbol'] = df['symbol'].value_counts().to_dict()
    
    # Count sentiments
    sentiment_counts = df['sentiment'].value_counts().to_dict()
    for sentiment in ['Positive', 'Negative', 'Neutral']:
        stats['sentiment_counts'][sentiment] = sentiment_counts.get(sentiment, 0)
    
    return stats

def display_dashboard():
    """Main dashboard display function."""
    # Dashboard header with app title and stats
    st.markdown('<div class="dashboard-title">Financial News & Sentiment Analysis</div>', unsafe_allow_html=True)
    
    # Sidebar for filters and system status
    st.sidebar.title("Controls & Status")
    
    # Check backend status
    backend_running = is_backend_running()
    api_keys = check_api_keys()
    watchlist = get_watchlist_from_config()
    
    # Display backend status section in sidebar
    st.sidebar.markdown("### System Status")
    
    # Backend status
    status_color = "status-active" if backend_running else "status-inactive"
    st.sidebar.markdown(f"""
    <div class="backend-status-box">
        <div><span class="{status_color} status-indicator"></span> <b>Backend Agent:</b> {'Running' if backend_running else 'Not Running'}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # API key status
    st.sidebar.markdown("#### API Keys")
    
    for api, info in api_keys.items():
        status_color = "status-active" if info['status'] == 'active' else "status-inactive" if info['status'] == 'inactive' else "status-unknown"
        name = "News API" if api == "news_api" else "Gemini LLM API" if api == "llm_api" else "Slack Webhook" 
        st.sidebar.markdown(f"""
        <div><span class="{status_color} status-indicator"></span> <b>{name}:</b> {info['message']}</div>
        """, unsafe_allow_html=True)
    
    # Display watchlist
    st.sidebar.markdown("#### Watchlist Symbols")
    if watchlist:
        st.sidebar.code(", ".join(watchlist))
    else:
        st.sidebar.warning("No watchlist symbols configured.")
    
    # Auto-refresh toggle
    st.sidebar.markdown("### Dashboard Settings")
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 
                                        min_value=10, max_value=300, value=60, 
                                        disabled=not auto_refresh)
    
    # Load data
    df = load_data()
    
    if df.empty:
        # Display instructions if no data
        st.info("No news articles found. The backend agent may not have processed any articles yet.")
        
        # Instructions and help
        st.markdown("### Getting Started")
        st.markdown("""
        1. Make sure your API keys are properly configured in `config/.env`
        2. Ensure the backend agent is running with `python -m src.main`
        3. Wait for articles to be processed (may take a few minutes)
        4. The dashboard will auto-refresh to show new articles
        """)
        
        # Run test data generator
        if st.button("Generate Test Data"):
            st.info("Running test script to generate sample data...")
            try:
                result = subprocess.run([sys.executable, 'test_news_fetch.py'], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Test data generated successfully! Refreshing dashboard...")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Error generating test data: {result.stderr}")
            except Exception as e:
                st.error(f"Error running test script: {str(e)}")
        
        # If autorefresh is enabled, wait and then rerun
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
        return
    
    # Processing stats
    stats = get_processing_stats(df)
    
    # Display statistics in expandable section
    with st.expander("📊 Processing Statistics", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", stats['total_articles'])
        with col2:
            st.metric("Unique Symbols", stats['total_symbols'])
        with col3:
            st.metric("Newest Article", stats['newest_article'])
        with col4:
            st.metric("Oldest Article", stats['oldest_article'])
        
        # Sentiment counts
        sentiment_counts = stats['sentiment_counts']
        total = sum(sentiment_counts.values())
        
        if total > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive", sentiment_counts['Positive'], f"{sentiment_counts['Positive']/total:.1%}")
            with col2:
                st.metric("Negative", sentiment_counts['Negative'], f"{sentiment_counts['Negative']/total:.1%}")
            with col3:
                st.metric("Neutral", sentiment_counts['Neutral'], f"{sentiment_counts['Neutral']/total:.1%}")
    
    # Split layout into main and side panels
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        # Display filter options based on available data
        available_symbols = sorted(df['symbol'].unique().tolist())
        available_sentiments = sorted(df['sentiment'].unique().tolist())
        
        # Filter controls in horizontal arrangement
        filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])
        
        with filter_col1:
            selected_symbols = st.multiselect("Filter by Symbols", available_symbols, default=[])
        
        with filter_col2:
            selected_sentiments = st.multiselect("Filter by Sentiment", available_sentiments, default=[])
        
        with filter_col3:
            if st.button("Clear Filters"):
                selected_symbols = []
                selected_sentiments = []
        
        # Apply filters
        filtered_df = df
        if selected_symbols:
            filtered_df = filtered_df[filtered_df['symbol'].isin(selected_symbols)]
        if selected_sentiments:
            filtered_df = filtered_df[filtered_df['sentiment'].isin(selected_sentiments)]
        
        # Display articles heading with counts
        st.subheader(f"Financial News Articles ({len(filtered_df)} of {len(df)} articles)")
        
        # Manual refresh button below filters
        refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 1, 1])
        with refresh_col2:
            if st.button("Refresh Data Now"):
                st.rerun()
        
        # Display articles
        if filtered_df.empty:
            st.info("No articles match your filter criteria.")
        else:
            # Display articles in cards
            for _, article in filtered_df.iterrows():
                render_article_card(article)
    
    with col_side:
        # Sentiment distribution chart
        st.subheader("Sentiment by Symbol")
        
        if not df.empty:
            try:
                # Create a sentiment count dataframe
                pivot_df = df.pivot_table(
                    index='symbol', 
                    columns='sentiment', 
                    values='title',
                    aggfunc='count',
                    fill_value=0
                ).reset_index()
                
                # Ensure all sentiment categories exist to avoid KeyError
                for sentiment in ['Positive', 'Negative', 'Neutral']:
                    if sentiment not in pivot_df.columns:
                        pivot_df[sentiment] = 0
                
                # Get only the sentiment columns that actually exist
                existing_sentiments = [col for col in ['Positive', 'Negative', 'Neutral'] if col in pivot_df.columns]
                
                if existing_sentiments:  # Only proceed if there are sentiment columns
                    # Reorganize for plotting
                    plot_df = pd.melt(
                        pivot_df, 
                        id_vars=['symbol'],
                        value_vars=existing_sentiments,
                        var_name='Sentiment',
                        value_name='Count'
                    )
                    
                    # Create the stacked bar chart
                    fig = px.bar(
                        plot_df,
                        x='symbol',
                        y='Count',
                        color='Sentiment',
                        color_discrete_map={
                            'Positive': '#0ECB81',
                            'Negative': '#F6465D',
                            'Neutral': '#808A9D'
                        },
                        title='',
                        labels={'symbol': 'Symbol', 'Count': 'Article Count', 'Sentiment': 'Sentiment'}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sentiment data available for charting.")
            except Exception as e:
                st.error(f"Error generating sentiment chart: {str(e)}")
                st.info("This usually happens when there's not enough data yet. Please wait for more articles to be processed.")
        
        # Recent Alerts section
        st.subheader("Recent Alerts")
        alerts = render_recent_alerts(df)
        
        if alerts:
            st.markdown('<div class="alert-history">', unsafe_allow_html=True)
            for alert in alerts:
                sentiment_class = f"sentiment-{alert['sentiment'].lower()}"
                st.markdown(f"""
                <div style="margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #e6e9ed;">
                    <div><span class="{sentiment_class}">{alert['sentiment']}</span> <span class="symbol-tag">{alert['symbol']}</span> <span style="color: #707A8A; font-size: 0.8em;">{alert['timestamp']}</span></div>
                    <div>{alert['title']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No alerts found. Alerts are generated for articles with Positive or Negative sentiment.")
    
    # Auto-refresh logic at the bottom
    if auto_refresh:
        # Display refresh timer placeholder
        refresh_placeholder = st.empty()
        
        # Calculate next refresh time
        next_refresh = datetime.now().timestamp() + refresh_interval
        
        # Update refresh timer
        while datetime.now().timestamp() < next_refresh:
            remaining = int(next_refresh - datetime.now().timestamp())
            refresh_placeholder.text(f"Refreshing in {remaining} seconds...")
            time.sleep(1)
        
        # Rerun the app after timer is done
        refresh_placeholder.empty()
        st.rerun()

if __name__ == "__main__":
    display_dashboard() 
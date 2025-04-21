#!/usr/bin/env python3
"""
Test script to generate realistic sample financial news articles
with sentiment analysis for demonstration purposes.
"""

import os
import json
import random
from datetime import datetime, timedelta
import sys

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)

# Path for processed news
processed_path = os.path.join(data_dir, 'processed_news.jsonl')

# Common financial symbols
symbols = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'META', 'NVDA', '$BTC', 'JPM', 'BAC']

# Sample topics
topics = [
    'Earnings Report', 'Product Launch', 'Executive Change', 
    'Market Analysis', 'Acquisition', 'Regulatory News',
    'Industry Trend', 'Financial Results', 'Strategic Partnership',
    'Investor Relations', 'Legal Development', 'Technology Innovation'
]

# Sample news sources
sources = [
    'Bloomberg', 'CNBC', 'Reuters', 'Wall Street Journal', 
    'Financial Times', 'MarketWatch', 'Business Insider',
    'Yahoo Finance', 'The Motley Fool', "Investor's Business Daily"
]

# Sample titles for different sentiments
title_templates = {
    'Positive': [
        "{symbol} Exceeds Earnings Expectations, Shares Soar",
        "{symbol} Announces Major Breakthrough in {topic}",
        "{symbol} Stock Rallies on Strong {topic}",
        "Analysts Upgrade {symbol} Following Impressive {topic}",
        "{symbol} Reports Record Growth in Quarterly {topic}",
        "{symbol} Secures Strategic Partnership for Future Growth",
        "Investors Bullish on {symbol} After Positive {topic}",
        "{symbol} Expands Market Share in Growing {topic} Sector",
        "{symbol} Dividend Increase Signals Management Confidence",
        "{symbol} Stock Hits All-Time High on {topic} News"
    ],
    'Negative': [
        "{symbol} Misses Earnings Targets, Shares Tumble",
        "{symbol} Faces Setback in {topic}, Investors Concerned",
        "{symbol} Stock Slides Following Disappointing {topic}",
        "Analysts Downgrade {symbol} Amid {topic} Challenges",
        "{symbol} Reports Declining Revenue in Latest Quarter",
        "{symbol} Announces Layoffs Amid Restructuring Efforts",
        "Investors Cautious on {symbol} After Negative {topic}",
        "{symbol} Loses Market Share to Competitors in {topic}",
        "{symbol} Cuts Forecast, Citing Market Uncertainties",
        "Regulatory Concerns Weigh on {symbol} Following {topic}"
    ],
    'Neutral': [
        "{symbol} Reports Mixed Results in Quarterly {topic}",
        "{symbol} Announces Leadership Transition, Impact Unclear",
        "{symbol} Maintains Market Position Despite {topic} Changes",
        "Analysts Hold Steady on {symbol} Following Recent {topic}",
        "{symbol} Adapts Strategy to Address {topic} Evolution",
        "{symbol} Completes Restructuring with Minimal Disruption",
        "Investors Assess {symbol}'s Position in Changing {topic} Landscape",
        "{symbol} Neither Gains nor Loses Ground in {topic} Sector",
        "{symbol} Meets Expectations in Recent {topic} Report",
        "{symbol} Navigates Market Uncertainty with Balanced Approach"
    ]
}

# Sample summaries for different sentiments
summary_templates = {
    'Positive': [
        "In a remarkable turn of events, {symbol} has reported quarterly earnings that significantly exceeded analyst expectations, driven primarily by strong performance in their {topic} division. The company's innovative approach to {topic} has yielded substantial gains, positioning them well for continued growth in the coming quarters. Investors have responded enthusiastically, with the stock seeing immediate positive movement.",
        "{symbol} has unveiled a groundbreaking development in {topic} that promises to revolutionize their industry position. Market analysts project this innovation could generate substantial new revenue streams and strengthen the company's competitive advantage. Early market response has been overwhelmingly favorable.",
        "The latest financial results from {symbol} show impressive growth across key metrics, with particularly strong performance in their {topic} segment. Management has raised guidance for the upcoming quarters, citing continued momentum and favorable market conditions. Analysts have responded by revising price targets upward.",
        "{symbol} has secured a major strategic partnership that strengthens their position in the {topic} market. This collaboration is expected to accelerate growth initiatives and expand market reach. Investors have responded positively to this development, seeing significant upside potential.",
        "Recent operational improvements at {symbol} have led to expanding profit margins and better-than-expected results in their {topic} business. Management's execution of their strategic plan has impressed analysts, who note the company is outperforming peers in key growth metrics."
    ],
    'Negative': [
        "{symbol} has reported quarterly results that fell short of market expectations, primarily due to challenges in their {topic} segment. Revenue growth has slowed significantly, and margins have compressed. Management has acknowledged the difficulties and announced a review of strategic options, but investor confidence has been shaken.",
        "In a disappointing development, {symbol} has encountered significant setbacks in their {topic} initiative. These challenges are expected to impact near-term performance and may require substantial additional investment to address. Market reaction has been swift, with the stock experiencing downward pressure.",
        "Competitive pressures have intensified for {symbol}, leading to a loss of market share in the critical {topic} segment. Analysts express concern about the company's ability to regain momentum without significant strategy adjustments. Management's response has been viewed as insufficient by many market participants.",
        "{symbol} has announced a major restructuring program following persistent underperformance in their {topic} division. The plan includes significant workforce reductions and facility closures. While necessary for long-term viability, these measures signal deeper problems than previously disclosed.",
        "Regulatory scrutiny has intensified for {symbol} regarding their {topic} practices. The potential for fines, operational restrictions, or mandatory changes to business models has created significant uncertainty. Legal experts suggest the resolution process could be protracted and costly."
    ],
    'Neutral': [
        "{symbol} has reported quarterly results largely in line with market expectations. While the {topic} division showed modest growth, challenges in other segments offset these gains. Management has maintained previous guidance, suggesting stable but not exceptional performance in the near term.",
        "The recent strategic shift announced by {symbol} regarding their approach to {topic} represents an evolutionary rather than revolutionary change. Analysts view the adjustments as sensible adaptations to market conditions rather than game-changing initiatives. The impact on financial performance is expected to be gradual.",
        "{symbol} has completed a planned leadership transition. The new management team has signaled continuity in major strategic initiatives while suggesting incremental improvements to execution in the {topic} area. Market reaction has been muted as investors await more concrete evidence of any changes in direction or results.",
        "Recent industry developments in {topic} have mixed implications for {symbol}. While creating some new opportunities, these changes also present adaptation challenges. The company appears well-positioned to manage these shifts, though no immediate material impact on financial results is expected.",
        "In their latest market update, {symbol} reported steady progress on key initiatives related to {topic}. Performance metrics show stability rather than acceleration or deterioration. Analysts view the company as reasonably valued at current levels, with balanced risk and reward potential."
    ]
}

def generate_random_datetime(days_back=30):
    """Generate a random datetime within the last N days"""
    now = datetime.now()
    random_days = random.uniform(0, days_back)
    random_seconds = random.uniform(0, 24 * 60 * 60)
    delta = timedelta(days=random_days, seconds=random_seconds)
    return (now - delta).isoformat()

def generate_article(symbol, sentiment=None):
    """Generate a realistic article for the given symbol with optional sentiment"""
    if not sentiment:
        sentiment = random.choice(['Positive', 'Negative', 'Neutral'])
    
    topic = random.choice(topics)
    source = random.choice(sources)
    
    title = random.choice(title_templates[sentiment]).format(symbol=symbol, topic=topic)
    summary = random.choice(summary_templates[sentiment]).format(symbol=symbol, topic=topic)
    
    # Create a real, working URL based on the source and symbol
    if source == 'Bloomberg':
        url = f"https://www.bloomberg.com/quote/{symbol}:US"
    elif source == 'Yahoo Finance':
        url = f"https://finance.yahoo.com/quote/{symbol}"
    elif source == 'CNBC':
        url = f"https://www.cnbc.com/quotes/{symbol}"
    elif source == 'MarketWatch':
        url = f"https://www.marketwatch.com/investing/stock/{symbol}"
    elif source == 'Reuters':
        url = f"https://www.reuters.com/markets/companies/{symbol}/"
    elif source == 'Financial Times':
        url = f"https://markets.ft.com/data/equities/tearsheet/summary?s={symbol}"
    elif source == 'Wall Street Journal':
        url = f"https://www.wsj.com/market-data/quotes/{symbol}"
    elif source == 'Business Insider':
        url = f"https://markets.businessinsider.com/stocks/{symbol}-stock"
    elif source == 'The Motley Fool':
        url = f"https://www.fool.com/quote/{symbol}"
    else:
        # Default to Yahoo Finance as fallback
        url = f"https://finance.yahoo.com/quote/{symbol}"
    
    # Handle special case for Bitcoin
    if symbol == '$BTC':
        url = f"https://www.coindesk.com/price/bitcoin/"
    
    return {
        'symbol': symbol,
        'title': title,
        'summary': summary,
        'url': url,
        'source': source,
        'published_at': generate_random_datetime(),
        'sentiment': sentiment,
        'topic': topic,
        'alert_triggered': sentiment in ['Positive', 'Negative'],
        'key_metrics': {
            'price_impact': random.uniform(-5.0, 5.0) if sentiment == 'Negative' else random.uniform(0.0, 5.0) if sentiment == 'Positive' else random.uniform(-1.0, 1.0),
            'confidence_score': random.uniform(0.7, 0.99),
            'market_relevance': random.uniform(0.5, 1.0)
        }
    }

def generate_sample_data(num_articles=50):
    """Generate a set of sample articles across different symbols and sentiments"""
    articles = []
    
    # Generate a balanced mix of sentiments for each symbol
    for symbol in symbols:
        # Ensure each symbol has at least one of each sentiment type
        for sentiment in ['Positive', 'Negative', 'Neutral']:
            articles.append(generate_article(symbol, sentiment))
    
    # Add more random articles to reach the desired total
    remaining = max(0, num_articles - len(articles))
    for _ in range(remaining):
        symbol = random.choice(symbols)
        articles.append(generate_article(symbol))
    
    # Sort by publication date (newest first)
    articles.sort(key=lambda x: x['published_at'], reverse=True)
    return articles

def save_to_jsonl(articles, filepath):
    """Save articles to JSONL file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(json.dumps(article) + '\n')
    print(f"Saved {len(articles)} articles to {filepath}")

def main():
    print("Generating sample financial news data...")
    articles = generate_sample_data(num_articles=50)
    save_to_jsonl(articles, processed_path)
    print("Sample data generation complete!")
    print(f"Data saved to: {processed_path}")
    
    # Print summary of generated data
    symbols_count = {}
    sentiment_count = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    
    for article in articles:
        symbol = article['symbol']
        sentiment = article['sentiment']
        
        if symbol not in symbols_count:
            symbols_count[symbol] = 0
        symbols_count[symbol] += 1
        sentiment_count[sentiment] += 1
    
    print("\nData Summary:")
    print(f"Total articles: {len(articles)}")
    print(f"Symbols covered: {len(symbols_count)}")
    print(f"Sentiment distribution: Positive: {sentiment_count['Positive']}, " +
          f"Negative: {sentiment_count['Negative']}, Neutral: {sentiment_count['Neutral']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
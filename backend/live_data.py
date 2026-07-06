import yfinance as yf
import feedparser
import logging

class LiveDataFetcher:
    """
    Fetches real-time market data and news using free public APIs.
    No API keys required.
    """
    
    @staticmethod
    def get_stock_data(ticker_symbol: str) -> dict:
        """Fetches live stock data using yfinance."""
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
                return {"status": "error", "message": f"Data Unavailable for {ticker_symbol}"}
                
            price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
            market_cap = info.get('marketCap', 'N/A')
            pe_ratio = info.get('trailingPE', 'N/A')
            recommendation = info.get('recommendationKey', 'N/A')
            
            return {
                "status": "success",
                "ticker": ticker_symbol.upper(),
                "price": price,
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "recommendation": recommendation,
                "source": "yfinance (Real-Time)"
            }
        except Exception as e:
            logging.error(f"Live data fetch failed for {ticker_symbol}: {e}")
            return {"status": "error", "message": "Data Unavailable"}

    @staticmethod
    def get_market_news(query: str = "business", limit: int = 3) -> list:
        """Fetches live news from Yahoo Finance RSS feed."""
        try:
            # Using Google News RSS as fallback/primary for broad queries
            # For Yahoo: https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US
            encoded_query = query.replace(" ", "%20")
            url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            
            if not feed.entries:
                return [{"title": "News Unavailable", "source": "N/A", "link": ""}]
                
            news_items = []
            for entry in feed.entries[:limit]:
                news_items.append({
                    "title": entry.title,
                    "source": getattr(entry, 'source', {}).get('title', 'Google News'),
                    "link": entry.link,
                    "published": getattr(entry, 'published', 'Recent')
                })
                
            return news_items
        except Exception as e:
            logging.error(f"News fetch failed for {query}: {e}")
            return [{"title": "News Unavailable", "source": "N/A", "link": ""}]

if __name__ == "__main__":
    # Test
    print(LiveDataFetcher.get_stock_data("AAPL"))
    print(LiveDataFetcher.get_market_news("Apple Stock"))

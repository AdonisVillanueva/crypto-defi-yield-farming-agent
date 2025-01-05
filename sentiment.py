import re
import requests
import os
from datetime import datetime, UTC, timedelta, timezone
from dotenv import load_dotenv
import streamlit as st
from bs4 import BeautifulSoup
import functools
import praw
from textblob import TextBlob
# Load environment variables from .env
load_dotenv()

# Detect if running in Streamlit
def is_streamlit():
    """Check if the code is running in a Streamlit environment."""
    return "streamlit" in os.environ.get("_", "")

# Use Streamlit caching if in Streamlit, otherwise use lru_cache
def conditional_cache(ttl=3600):
    """Decorator to use Streamlit caching in Streamlit or lru_cache otherwise."""
    if is_streamlit():
        import streamlit as st
        return st.cache_data(ttl=ttl)
    else:
        return functools.lru_cache(maxsize=1)

class Sentiment:
    def __init__(self):
        """
        Initializes the SentimentAgent class with API endpoints and keys.
        - Santiment API: For crypto-specific sentiment analysis.
        - Fear & Greed Index: For overall crypto market sentiment.
        - VIX Index: For traditional finance (TradFi) sentiment.
        - NewsAPI: For news-based sentiment analysis.
        """
        # API Endpoints
        self.altcoin_season_url = "https://www.blockchaincenter.net/en/altcoin-season-index/"
        self.santiment_url = "https://api.santiment.net/graphql"
        self.santiment_api_key = os.getenv("SANTIMENT_API_KEY")  # Get API key from .env
        self.fear_greed_url = "https://api.alternative.me/fng/"  # Crypto Fear & Greed Index
        self.yahoo_url = "https://finance.yahoo.com/quote/%5EVIX/"
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

    @conditional_cache(ttl=3600)  # Replace @st.cache_data with @conditional_cache
    def get_fear_and_greed_index(_self):
        """Fetch the Fear & Greed Index from alternativec.me."""
        try:
            url = _self.fear_greed_url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses

            # Parse the JSON response
            data = response.json()
            if "data" not in data or not data["data"]:
                raise ValueError("No Fear & Greed Index data found in response")

            # Extract the latest Fear & Greed Index value
            latest_data = data["data"][0]
            value = int(latest_data["value"])
            classification = latest_data["value_classification"]
            timestamp = int(latest_data["timestamp"])  # Ensure timestamp is an integer
            readable_date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%B %d, %Y, %H:%M:%S UTC')
            return {
                "value": value,
                "classification": classification,
                "date_fetched": readable_date
            }
        except Exception as e:
            print(f"Failed to fetch Fear & Greed Index data: {e}")
            return None

    @conditional_cache(ttl=3600)  # Replace @st.cache_data with @conditional_cache
    def get_tradfi_sentiment(_self):
        """Fetch and analyze TradFi sentiment (VIX)."""
        try:
            yahoo_url = _self.yahoo_url
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(yahoo_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract VIX value, change, and percent change from Yahoo Finance
            vix_element = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
            if not vix_element:
                raise ValueError("VIX value element not found in Yahoo Finance HTML")
            
            vix_value_str = vix_element.text
            vix_value = float(vix_value_str.replace(',', ''))  # Remove commas and convert to float
            
            # Extract change and percent change
            change = float(soup.find('fin-streamer', {'data-field': 'regularMarketChange'}).text)
            change_percent = float(soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'}).text.strip('()%'))
            
            # Analyze VIX value
            analysis = _self._analyze_vix_value(vix_value)
            
            return {
                'value': vix_value,
                'change': change,  # Add change
                'change_percent': change_percent,  # Add percent change
                'analysis': analysis,
                'source': 'Yahoo Finance'
            }
        except Exception as e:
            print(f"Yahoo Finance fallback failed: {e}")
            return None

    def _analyze_vix_value(self, vix_value):
        """Helper method to analyze VIX value."""
        if vix_value >= 30:
            return "High Volatility (Market Fear in TradFi - Bearish)"
        elif vix_value >= 20:
            return "Moderate Volatility (Market Caution in TradFi - Neutral)"
        else:
            return "Low Volatility (Market Complacency in TradFi - Bullish)"
        
    @conditional_cache(ttl=3600)  # Replace @st.cache_data with @conditional_cache
    def get_reddit_sentiment(_self, subreddit="cryptocurrency", limit=10):
        """
        Fetch and analyze sentiment from a subreddit.
        
        Args:
            subreddit (str): The subreddit to analyze (default: "cryptocurrency").
            limit (int): Number of posts to analyze (default: 10).
        
        Returns:
            dict: A dictionary containing average sentiment and sample posts.
        """
        try:
            # Fetch posts from the subreddit
            subreddit = _self.reddit.subreddit(subreddit)
            posts = subreddit.new(limit=limit)

            # Analyze sentiment for each post
            sentiment_scores = []
            sample_posts = []

            for post in posts:
                # Analyze post title
                title_blob = TextBlob(post.title)
                title_sentiment = title_blob.sentiment.polarity

                # Analyze post comments (top 5 comments)
                post.comments.replace_more(limit=0)
                comment_sentiments = []
                for comment in post.comments[:5]:
                    comment_blob = TextBlob(comment.body)
                    comment_sentiments.append(comment_blob.sentiment.polarity)

                # Average sentiment for the post
                post_sentiment = (title_sentiment + sum(comment_sentiments)) / (1 + len(comment_sentiments))
                sentiment_scores.append(post_sentiment)

                # Store sample post data
                sample_posts.append({
                    "title": post.title,
                    "score": post.score,
                    "sentiment": post_sentiment
                })

            # Calculate average sentiment
            average_sentiment = sum(sentiment_scores) / len(sentiment_scores)

            return {
                "average_sentiment": average_sentiment
                #"sample_posts": sample_posts
            }

        except Exception as e:
            print(f"Failed to fetch Reddit sentiment: {e}")
            return None

    @conditional_cache(ttl=3600)  # Replace @st.cache_data with @conditional_cache
    def get_santiment_data(_self, crypto_slug="ethereum", metric="daily_active_addresses"):
        """Fetch sentiment data from Santiment API."""
        try:
            # Define date range (from 7 days ago to now)
            to_date = datetime.now(UTC)
            from_date = to_date - timedelta(days=7)

            # GraphQL query
            query = """
            {
                getMetric(metric: "%s") {
                    timeseriesData(
                        slug: "%s",
                        from: "%s",
                        to: "%s",
                        interval: "1d"
                    ) {
                        datetime
                        value
                    }
                }
            }
            """ % (metric, crypto_slug, from_date.isoformat(), to_date.isoformat())

            # Headers with API key
            headers = {
                "Authorization": f"Apikey {_self.santiment_api_key}",
                "Content-Type": "application/json",
            }

            # Make the API request
            response = requests.post(_self.santiment_url, json={"query": query}, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses

            # Parse the response
            data = response.json()

            # Handle error response
            if "errors" in data:
                print(f"Santiment API error: {data['errors'][0]['message']}")
                return None

            # Extract the latest sentiment value
            if "data" not in data or not data["data"]:
                raise ValueError("No data returned from Santiment API")

            timeseries_data = data["data"]["getMetric"]["timeseriesData"]
            if not timeseries_data:
                raise ValueError("No timeseries data found")

            latest_data = timeseries_data[0]
            return latest_data["value"]

        except Exception as e:
            print(f"Failed to fetch Santiment data: {e}")
            return None
        
    # Fetch Altcoin Season data with caching
    @conditional_cache(ttl=3600)  # Replace @st.cache_data with @conditional_cache
    def get_altcoin_season_index(_self):
        """Fetch the Altcoin Season Index from the webpage."""
        try:
            url = _self.altcoin_season_url
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find the Altcoin Season Index text
            index_text = soup.find("button", class_="nav-link timeselect active").text.strip()  # Update the selector
            match = re.search(r"\((\d+)\)", index_text)
            if match:
                value = int(match.group(1))
                season_message = "Altcoin Season" if value > 75 else "Bitcoin Season"
                return {
                    "value": value,
                    "season": season_message
                }
            else:
                st.warning("Altcoin Season Index value not found on the page.")
                return None
        except Exception as e:
            st.error(f"Error fetching Altcoin Season Index: {e}")
            return None
        
    def determine_market_condition(_self, crypto_slug="ethereum"):
        """
        Determine the overall market condition based on multiple data sources.
        
        Returns:
            str: The overall market condition (e.g., "bullish", "bearish", "neutral").
        """
        # Fetch data from all sources
        santiment_data = _self.get_santiment_data(crypto_slug=crypto_slug, metric="daily_active_addresses")
        if santiment_data is None:
            # Fallback to Ethereum if no data is found for the provided crypto_slug
            print(f"No Santiment data found for {crypto_slug}, falling back to Ethereum...")
            santiment_data = _self.get_santiment_data(crypto_slug="ethereum", metric="daily_active_addresses")

        fear_and_greed = _self.get_fear_and_greed_index()
        tradfi_sentiment = _self.get_tradfi_sentiment()
        reddit_sentiment = _self.get_reddit_sentiment(subreddit="cryptocurrency", limit=10)

        # Print fetched data for debugging
        print("Santiment Data:", santiment_data)
        print("Fear & Greed Index:", fear_and_greed)
        print("TradFi Sentiment:", tradfi_sentiment)
        print("Reddit Sentiment:", reddit_sentiment)

        # Determine weights for each data source
        weights = {
            "santiment": 0.3,
            "fear_and_greed": 0.3,
            "tradfi": 0.1,
            "reddit": 0.3
        }

        # Calculate weighted scores
        santiment_score = santiment_data / 10000 if santiment_data else 0  # Normalize Santiment data
        fear_and_greed_score = fear_and_greed["value"] / 100 if fear_and_greed else 0  # Normalize Fear & Greed Index
        tradfi_score = tradfi_sentiment["value"] / 100 if tradfi_sentiment else 0  # Normalize TradFi Sentiment
        reddit_score = reddit_sentiment["average_sentiment"] if reddit_sentiment else 0  # Use Reddit sentiment directly

        # Calculate overall score
        overall_score = (
            santiment_score * weights["santiment"] +
            fear_and_greed_score * weights["fear_and_greed"] +
            tradfi_score * weights["tradfi"] +
            reddit_score * weights["reddit"]
        )

        # Determine market condition based on overall score
        if overall_score > 0.6:
            return "bullish"
        elif overall_score < 0.4:
            return "bearish"
        else:
            return "neutral"

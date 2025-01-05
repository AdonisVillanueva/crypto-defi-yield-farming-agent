from sentiment import Sentiment

# Initialize the Sentiment class
sentiment_agent = Sentiment()

# Test Reddit Sentiment Analysis
def test_get_reddit_sentiment():
    print("Testing Reddit Sentiment Analysis...")
    subreddit = "cryptocurrency"
    reddit_sentiment = sentiment_agent.get_reddit_sentiment(subreddit=subreddit, limit=5)
    if reddit_sentiment:
        print(f"Average Sentiment: {reddit_sentiment['average_sentiment']} (A positive number is bullish and negative is bearish)")
    else:
        print("Warning: Failed to fetch Reddit sentiment.")
# Test Fear & Greed Index
def test_get_fear_and_greed_index():
    print("Testing Fear & Greed Index...")
    fear_and_greed_index = sentiment_agent.get_fear_and_greed_index()
    if fear_and_greed_index:
        print("Fear & Greed Index Data:")
        print(f"Value: {fear_and_greed_index['value']}")
        print(f"Classification: {fear_and_greed_index['classification']}")
        print(f"Timestamp: {fear_and_greed_index['date_fetched']}")
    else:
        print("Warning: Failed to fetch Fear & Greed Index data.")
    print("---")
# Test TradFi Sentiment
def test_get_tradfi_sentiment():
    print("Testing TradFi Sentiment...")
    tradfi_sentiment = sentiment_agent.get_tradfi_sentiment()
    if tradfi_sentiment:
        print("TradFi Sentiment Data:")
        print(f"Value: {tradfi_sentiment['value']}")
        print(f"Change: {tradfi_sentiment['change']}")
        print(f"Change Percent: {tradfi_sentiment['change_percent']}")
        print(f"Analysis: {tradfi_sentiment['analysis']}")
        print(f"Source: {tradfi_sentiment['source']}")
    else:
        print("Warning: Failed to fetch TradFi sentiment.")
    print("---")
# Test Santiment Data Fetching
def test_get_santiment_data():
    print("Testing Santiment Data Fetching...")
    crypto_slug = "ethereum"  # Default to Ethereum
    metric = "daily_active_addresses"  # Default metric
    santiment_data = sentiment_agent.get_santiment_data(crypto_slug=crypto_slug, metric=metric)
    if santiment_data is not None:
        print(f"Santiment Data for {crypto_slug} ({metric}):")
        print(f"Latest Value: {santiment_data}")
    else:
        print("Warning: Failed to fetch Santiment data.")
    print("---")
# Test Altcoin Season Index
def test_get_altcoin_season_index():
    print("Testing Altcoin Season Index...")
    altcoin_season_data = sentiment_agent.get_altcoin_season_index()
    if altcoin_season_data:
        print("Altcoin Season Index Data:")
        print(f"Value: {altcoin_season_data['value']}")
        print(f"Season: {altcoin_season_data['season']}")
    else:
        print("Warning: Failed to fetch Altcoin Season Index data.")
    print("---")
    # Test Determine Market Condition
# Test Determine Market Condition
def test_determine_market_condition():
    print("Testing Determine Market Condition...")
    market_condition = sentiment_agent.determine_market_condition()
    if market_condition:
        print(f"Market Condition: {market_condition}")
    else:
        print("Warning: Failed to determine market condition.")
    print("---")
# Run all tests
if __name__ == "__main__":
    test_get_reddit_sentiment()
    test_get_santiment_data()
    test_get_fear_and_greed_index()
    test_get_tradfi_sentiment()
    test_get_altcoin_season_index()
    test_determine_market_condition()
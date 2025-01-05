from sentiment import Sentiment  # Assuming the class is in sentiment.py

def test_news_sentiment():
    # Initialize the Sentiment class
    sentiment_agent = Sentiment()

    # Test with a specific cryptocurrency
    crypto = "bitcoin"
    sentiment_score = sentiment_agent.get_news_sentiment(crypto=crypto)

    # Print the result
    print(f"Sentiment Score for {crypto}: {sentiment_score}")

    # Debug: Print intermediate results (optional)
    # Uncomment the following lines to debug the scraping logic
    # print("\nScraped Articles:")
    # for article in sentiment_agent.get_scraped_articles(crypto=crypto):
    #     print(f"Title: {article['title']}")
    #     print(f"Description: {article['description']}")
    #     print()

if __name__ == "__main__":
    test_news_sentiment() 
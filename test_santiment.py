import os
from datetime import datetime, timedelta, UTC
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Santiment API details
SANTIMENT_API_KEY = os.getenv("SANTIMENT_API_KEY")
SANTIMENT_URL = "https://api.santiment.net/graphql"

def test_santiment_api(crypto_slug="ethereum", metric="SAN_SOCIAL_VOLUME"):
    """Test the Santiment API with a specific cryptocurrency and metric."""
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
            "Authorization": f"Apikey {SANTIMENT_API_KEY}",
            "Content-Type": "application/json",
        }

        # Make the API request
        response = requests.post(SANTIMENT_URL, json={"query": query}, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the response
        data = response.json()
        print("Raw API Response:", data)  # Debug: Print raw response

        if "data" not in data or not data["data"]:
            raise ValueError("No data returned from Santiment API")

        # Extract the latest sentiment value
        timeseries_data = data["data"]["getMetric"]["timeseriesData"]
        if not timeseries_data:
            raise ValueError("No timeseries data found")

        latest_data = timeseries_data[0]
        print("Santiment API Response:")
        print(f"Datetime: {latest_data['datetime']}")
        print(f"Value: {latest_data['value']}")

    except Exception as e:
        print(f"Failed to fetch Santiment data: {e}")

if __name__ == "__main__":
    test_santiment_api()
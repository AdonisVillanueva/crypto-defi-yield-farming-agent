import streamlit as st
import datetime
import time
import json
import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
# Load environment variables from .env
load_dotenv()

class CryptoDeFiYieldFarmingAgent:
    def __init__(self):
        self.fear_greed_url = "https://api.alternative.me/fng/"
        self.vix_url = "https://finance.yahoo.com/quote/%5EVIX/"
        self.altcoin_season_url = "https://www.blockchaincenter.net/en/altcoin-season-index/"
        self.community_file = "community/community_strategies.json"
        self.community_strategies = self.load_community_strategies()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")  # Get API key from .env
        self.deepseek_api_url = "https://api.deepseek.com"  # Example endpoint

    def load_community_strategies(self):
        """Load community strategies from a JSON file."""
        try:
            # Ensure the 'community' directory exists
            os.makedirs("community", exist_ok=True)
            
            # Check if the file exists
            if not os.path.exists(self.community_file):
                # Create an empty file if it doesn't exist
                with open(self.community_file, "w") as file:
                    json.dump([], file)
                return []
            
            # Load strategies from the file
            with open(self.community_file, "r") as file:
                return json.load(file)
        except Exception as e:
            st.error(f"Error loading community strategies: {e}")
            return []

    def save_community_strategies(self):
        """Save community strategies to a JSON file."""
        try:
            with open(self.community_file, "w") as file:
                json.dump(self.community_strategies, file, indent=4)
        except Exception as e:
            st.error(f"Error saving community strategies: {e}")

    def get_fear_and_greed_index(self):
        """Fetch Crypto Fear & Greed Index."""
        try:
            response = requests.get(self.fear_greed_url)
            data = response.json()
            if response.status_code == 200:
                latest_data = data['data'][0]
                return {
                    'value': int(latest_data['value']),
                    'classification': latest_data['value_classification']
                }
            return None
        except Exception as e:
            st.error(f"Error fetching Fear & Greed Index: {e}")
            return None

    def get_altcoin_season_index(self):
        """Fetch Altcoin Season Index from BlockchainCenter and determine season."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(self.altcoin_season_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the Altcoin Season Index value using its unique style attributes
            index_div = soup.find('div', style="font-size:88px;  color:#345C99;position:relative;top:56px;left:calc(47% - 46px)")
            if index_div:
                index_value = int(index_div.text.strip())
                # Determine season based on index value
                if index_value > 75:
                    season_message = "Altcoin Season"
                else:
                    season_message = "Bitcoin Season"
                return {
                    'value': index_value,
                    'season': season_message
                }
            else:
                print("Altcoin Season Index value not found on the page.")
                return None
        except Exception as e:
            print(f"Error fetching Altcoin Season Index: {e}")
            return None

    def get_vix_index(self):
        """Fetch CBOE Volatility Index (VIX) from Yahoo Finance."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(self.vix_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract VIX value
            vix_value = float(soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text)
            
            # Extract change and percent change
            change = float(soup.find('fin-streamer', {'data-field': 'regularMarketChange'}).text)
            change_percent = float(soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'}).text.strip('()%'))
            
            return {
                'value': vix_value,
                'change': change,
                'change_percent': change_percent,
                'analysis': self.get_vix_analysis(vix_value)
            }
        except Exception as e:
            st.error(f"Error fetching VIX Index: {e}")
            return None

    def get_vix_analysis(self, vix_value):
        """Analyze VIX value."""
        if vix_value >= 30:
            return "High Volatility (Market Fear)"
        elif vix_value >= 20:
            return "Moderate Volatility (Market Caution)"
        else:
            return "Low Volatility (Market Complacency)"

    def save_community_strategies(self):
        """Save community strategies to a JSON file."""
        with open(self.community_file, "w") as file:
            json.dump(self.community_strategies, file)

    def call_deepseek_api(self, prompt):
        """Call the DeepSeek API to generate insights or analyze data."""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",  # Required model name
            "messages": [
                {"role": "system", "content": "You are a Crypto Finance Analyst specializing in DeFi and Yield Farming."},
                {"role": "user", "content": prompt}
            ],
            "stream": False  # Set to True for streaming responses
        }
        response = requests.post(
            f"{self.deepseek_api_url}/chat/completions",  # Correct endpoint
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"Failed to call DeepSeek API: {response.status_code}")
            return None

    def share_strategy(self, crypto, strategy, market_condition):
        """Share a strategy with the community."""
        if not crypto or not strategy:
            st.error("Please provide both a cryptocurrency and a strategy.")
            return

        self.community_strategies.append({
            "crypto": crypto,
            "strategy": strategy,
            "market_condition": market_condition,  # Automatically use the current market condition
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_community_strategies()
        st.success("Your strategy has been shared with the community!")

    def analyze_market(self):
        """Analyze combined market sentiment."""
        crypto_data = self.get_fear_and_greed_index()
        vix_data = self.get_vix_index()
        altcoin_season_data = self.get_altcoin_season_index()
        
        if not crypto_data or not vix_data or not altcoin_season_data:
            return "Unable to fetch market data"
        
        # Map Fear & Greed Index to bullish/bearish
        if crypto_data['value'] >= 55:
            market_condition = "bullish"
        else:
            market_condition = "bearish"
        
        return {
            'crypto': crypto_data,
            'altcoin_season': altcoin_season_data,
            'market_condition': market_condition,
            'vix_data': vix_data
        }

    def get_crypto_price(self, crypto):
        """Fetch the current price of a cryptocurrency using CoinGecko API."""
        try:
            # Map crypto names to CoinGecko IDs
            crypto_map = {
                "BTC": "bitcoin",
                "Ethereum": "ethereum",
                "Solana": "solana",
                "Sui": "sui",
                # Add more mappings as needed
            }

            # Get the CoinGecko ID for the crypto
            crypto_id = crypto_map.get(crypto, crypto.lower())

            # Fetch price from CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract and return the price
            price_data = response.json()
            if crypto_id in price_data and "usd" in price_data[crypto_id]:
                return price_data[crypto_id]["usd"]
            else:
                st.error(f"Price data not found for {crypto}")
                return None
        except Exception as e:
            st.error(f"Failed to fetch price for {crypto}: {e}")
            return None

    def get_recommendation(self, crypto, market_condition):
        """Generate DeFi and Yield Farming strategies using DeepSeek API."""
        if crypto in ["BTC", "Ethereum", "Solana", "Sui"]:
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for {crypto}. 
            Focus only on {crypto} and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            If {crypto} is BTC and the market condition is bullish, include the following strategy on the Base network:
            1. Wrap BTC to cbBTC (Coinbase BTC) on Base.
            2. Lend cbBTC on Aave (Base network) and use it as collateral.
            3. Borrow a stable asset like USDC against this collateral on Aave (Base network).
            4. Take the borrowed USDC and provide liquidity in a high APY pool like USDC/ETH concentrated pool in Aerodrome on Base L2.
            5. The interest earned should cover the borrowed APR, and you also get the advantage of BTC's price appreciation in a bull market.

            If {crypto} is BTC and the market condition is bearish, include the following strategy:
            1. Convert BTC to USDC.
            2. Lend USDC on Aave and use it as collateral.
            3. Borrow a depreciating asset like BTC or ETH against this collateral on Aave.
            4. Convert the borrowed BTC/ETH back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            If {crypto} is Ethereum and the market condition is bullish, include strategies such as:
            - Staking ETH in Lido or Rocket Pool for staking rewards.
            - Providing liquidity in Uniswap V3 or Curve pools.
            - Leveraging ETH in Aave or Compound for borrowing and yield farming.

            If {crypto} is Ethereum and the market condition is bearish, include the following strategy:
            1. Convert ETH to USDC.
            2. Lend USDC on Aave and use it as collateral.
            3. Borrow a depreciating asset like ETH or BTC against this collateral on Aave.
            4. Convert the borrowed ETH/BTC back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            If {crypto} is Solana and the market condition is bullish, include strategies such as:
            - Staking SOL in native validators or platforms like Marinade Finance.
            - Providing liquidity in Raydium or Orca pools.
            - Leveraging SOL in lending protocols like Solend.

            If {crypto} is Solana and the market condition is bearish, include the following strategy:
            1. Convert SOL to USDC.
            2. Lend USDC on Aave or Solend and use it as collateral.
            3. Borrow a depreciating asset like SOL or ETH against this collateral.
            4. Convert the borrowed SOL/ETH back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Raydium or Orca for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            If {crypto} is Sui and the market condition is bullish, include strategies such as:
            - Staking SUI in native validators.
            - Providing liquidity in AlphaFi's stSUI-USDC pair, which is currently returning over 400% APR.
            - Leveraging SUI in lending protocols on Sui.

            If {crypto} is Sui and the market condition is bearish, include the following strategy:
            1. Convert SUI to USDC.
            2. Lend USDC on Aave or Sui lending protocols and use it as collateral.
            3. Borrow a depreciating asset like SUI or ETH against this collateral.
            4. Convert the borrowed SUI/ETH back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like AlphaFi for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            Be concise and actionable.
            """
        else:
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for {crypto}. 
            Focus only on {crypto} and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            For {crypto}, consider the following general strategies:
            - Staking {crypto} in native protocols or platforms.
            - Providing liquidity in decentralized exchanges.
            - Leveraging {crypto} in lending protocols for borrowing and yield farming.

            If the market condition is bullish, focus on strategies that maximize returns, such as:
            - Providing liquidity in high APY pools.
            - Leveraging {crypto} for borrowing and yield farming.
            - Staking {crypto} for rewards.

            If the market condition is bearish, focus on strategies that minimize risk, such as:
            - Converting {crypto} to stablecoins like USDC.
            - Lending stablecoins and borrowing depreciating assets.
            - Providing liquidity in stablecoin pairs.

            Be concise and actionable.
            """
        return self.call_deepseek_api(prompt)

    def explain_risk_score(self, crypto, risk_score):
        """Provide a risk explanation using DeepSeek API."""
        prompt = f"Explain the risk score of {risk_score}/10 for DeFi strategies involving {crypto}."
        return self.call_deepseek_api(prompt)

    def view_community_strategies(self, crypto, market_condition):
        """Display community strategies filtered by crypto and market condition."""
        if not self.community_strategies:
            st.warning("No strategies have been shared yet.")
            return

        # Filter strategies for the current crypto and market condition
        filtered_strategies = [
            strategy for strategy in self.community_strategies
            if strategy["crypto"].lower() == crypto.lower() and strategy["market_condition"] == market_condition
        ]

        if not filtered_strategies:
            st.warning(f"No {market_condition} strategies found for {crypto}.")
            return

        st.subheader(f"Community {market_condition.capitalize()} Strategies for {crypto}")
        for i, strategy in enumerate(filtered_strategies, 1):
            st.write(f"### Strategy #{i}")
            st.write(f"**date_added:** {strategy['date_added']}")
            st.write(f"**Strategy:**\n{strategy['strategy']}")
            st.write("---")  # Add a separator between strategies

    def run(self):
        """Run the Crypto DeFi & Yield Farming Agent."""
        st.title("Agent YieldDeFi")
        st.sidebar.header("Menu")

        # Cryptocurrency Selection
        crypto = st.sidebar.selectbox(
            "Select a cryptocurrency",
            ["BTC", "Ethereum", "Solana", "Sui", "Custom"]
        )
        if crypto == "Custom":
            crypto = st.sidebar.text_input("Enter the cryptocurrency you'd like to analyze:")
            if not crypto:
                st.error("Please enter a valid cryptocurrency.")
                return

        # Initialize market_analysis as None
        market_analysis = None

        # Analyze Button
        if st.sidebar.button("Analyze"):
            st.subheader(f"Analysis for {crypto}")

            # Fetch and display crypto price
            crypto_price = self.get_crypto_price(crypto)
            if crypto_price is not None:  # Explicitly check for None
                st.write(f"**Current Price:** ${crypto_price:,.2f}")  # Format with commas and 2 decimal places
            else:
                st.warning("Could not fetch price data for this cryptocurrency.")

            # Fetch and display Fear & Greed Index
            fear_greed_data = self.get_fear_and_greed_index()
            if fear_greed_data:
                st.markdown(
                    f"**Fear & Greed Index:** {fear_greed_data['value']} ({fear_greed_data['classification']}) "
                    f"<span style='color: gray; font-size: 0.9em;'>(Measures market sentiment from 0 = Extreme Fear to 100 = Extreme Greed)</span>",
                    unsafe_allow_html=True
                )

            # Analyze market and display recommendation
            market_analysis = self.analyze_market()
            st.write(f"**Market Condition:** {market_analysis['market_condition']}")

            # Display VIX data
            vix_data = market_analysis['vix_data']
            st.write(f"**VIX Index:** {vix_data['value']} ({vix_data['analysis']})")
            st.write(f"**Change:** {vix_data['change']} ({vix_data['change_percent']}%)")

            # Generate recommendation with progress bar
            progress_bar = st.progress(0)
            processing_message = st.empty()  # Use a placeholder for the processing message
            processing_message.write("**Generating recommendations...**")  # Indicate processing
            recommendation = None

            # Simulate progress while waiting for recommendation
            def update_progress(progress_bar, processing_message):
                for percent_complete in range(100):
                    time.sleep(0.1)  # Simulate delay (adjust as needed)
                    progress_bar.progress(percent_complete + 1)
                processing_message.empty()  # Remove "Processing recommendation..." message

            # Generate recommendation
            recommendation = self.get_recommendation(crypto, market_analysis['market_condition'])

            # Update progress bar after recommendation is done
            update_progress(progress_bar, processing_message)

            # Display recommendation
            st.write("**Recommendation:**")
            st.markdown(recommendation.replace("\n", "  \n"))

            # Display risk score with red line and indicator
            risk_score = 5  # Example risk score (you can calculate this dynamically)
            st.write(f"**Risk Score:** {risk_score}/10")
            st.markdown(
                f"""
                <style>
                .risk-bar {{
                    width: 100%;
                    height: 10px;
                    background: linear-gradient(to right, green 0%, yellow 50%, red 100%);
                    position: relative;
                    margin-top: 5px;
                }}
                .risk-indicator {{
                    width: 2px;
                    height: 15px;
                    background: black;
                    position: absolute;
                    left: {risk_score * 10}%;
                    top: -2.5px;
                }}
                </style>
                <div class="risk-bar">
                    <div class="risk-indicator"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            risk_explanation = self.explain_risk_score(crypto, risk_score)
            st.write(f"**Risk Explanation:** {risk_explanation}")

            # Notifications
            if vix_data['value'] > 30:
                st.warning("High Volatility Detected! Consider reducing risk exposure.")

            # Post-recommendation options
            st.subheader("Next Steps")
            if st.button(f"View Community {market_analysis['market_condition'].capitalize()} Strategies for {crypto}"):
                self.view_community_strategies(crypto, market_analysis['market_condition'])

        # Share Your Strategy Section (only show if market_analysis exists)
        if market_analysis:
            st.subheader(f"Share Your {market_analysis['market_condition'].capitalize()} Strategy for {crypto}")
            personal_strategy = st.text_area("Enter your personal strategy (Plain English):")
            if st.button("Submit Strategy"):
                if personal_strategy.strip():  # Ensure the strategy is not empty
                    self.share_strategy(crypto, personal_strategy, market_analysis['market_condition'])  # Pass market condition
                else:
                    st.error("Please enter a valid strategy before submitting.")

if __name__ == "__main__":
    agent = CryptoDeFiYieldFarmingAgent()
    agent.run()
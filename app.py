import streamlit as st
import datetime
import time
import json
import requests
from dotenv import load_dotenv
from sentiment import Sentiment
import os
from bs4 import BeautifulSoup
import re
# Load environment variables from .env
load_dotenv()

# Initialize Sentiment class
@st.cache_resource  # Cache the Sentiment instance
def get_sentiment_agent():
    return Sentiment()

class CryptoDeFiYieldFarmingAgent:
    #This is for the AI Model to evaluate the strategies
    STRATEGY_EVALUATION_CRITERIA = """
    Be concise, actionable, provide pros and cons, and a rating (1-10) of what you think for each strategy. 
    Include a link to a website or a YouTube video explaining the strategy. 
    Do not include deep dives if it's irrelevant, not helpful, or missing content.
    """
    def __init__(self):        
        self.community_file = "community/community_strategies.json"
        self.community_strategies = self.load_community_strategies()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")  # Get API key from .env
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL")
        self.coinmarketcap_api_key = os.getenv("COINMARKETCAP_API_KEY")  # Get API key from .env
        # Initialize Sentiment agent
        self.sentiment_agent = Sentiment()
        #Crypto string mapping to slug
        self.crypto_map = {
            "BTC": "bitcoin",
            "Ethereum": "ethereum",
            "Solana": "solana",
            "Sui": "sui",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "Cardano": "cardano",
            "Dogecoin": "dogecoin",
            "Avalanche": "avalanche-2",
            "Polkadot": "polkadot",
            "Polygon": "matic-network",
            "Litecoin": "litecoin",
            "Chainlink": "chainlink",
            "Uniswap": "uniswap",
            "Tron": "tron",
            "Atom": "cosmos",
            "Monero": "monero",
            "Ethereum Classic": "ethereum-classic",
            "Stellar": "stellar",
            "Algorand": "algorand",
            "Filecoin": "filecoin",
            "Tezos": "tezos",
            "Aave": "aave",
            "Compound": "compound-governance-token",
            "Shiba Inu": "shiba-inu",
            "NEAR Protocol": "near",
            "Fantom": "fantom",
            "Optimism": "optimism",
            "Arbitrum": "arbitrum",
            "Aptos": "aptos",
            "Mina": "mina-protocol",
            "Flow": "flow",
            "Hedera": "hedera-hashgraph",
            "Klaytn": "klay-token",
            "Zilliqa": "zilliqa",
            "Theta": "theta-token",
            "Axie Infinity": "axie-infinity",
            "Decentraland": "decentraland",
            "The Sandbox": "the-sandbox",
            "Gala": "gala",
            "Enjin Coin": "enjincoin",
            "Chiliz": "chiliz",
            "Immutable X": "immutable-x",
            "Loopring": "loopring",
            "Harmony": "harmony",
            "Kusama": "kusama",
            "Elrond": "elrond-erd-2",
            "Celo": "celo",
            "Cosmos": "cosmos",
            "UMA": "uma",
            "Band Protocol": "band-protocol",
            "API3": "api3",
            "DIA": "dia-data",
            "Tellor": "tellor",
            "NMR": "numeraire",
            "Ocean Protocol": "ocean-protocol",
            "Fetch.ai": "fetch-ai",
            "SingularityNET": "singularitynet",
            "Numeraire": "numeraire",
            "Bancor": "bancor",
            "Balancer": "balancer",
            "Curve DAO Token": "curve-dao-token",
            "SushiSwap": "sushi",
            "1inch": "1inch",
            "Yearn.finance": "yearn-finance",
            "Maker": "maker",
            "Compound": "compound-governance-token",
            "Synthetix": "synthetix-network-token",
            "Ren": "ren",
            "Reserve Rights": "reserve-rights-token",
        }

    def load_community_strategies(self):
        """Load community strategies from a JSON file."""
        try:
            # Ensure the 'community' directory exists
            os.makedirs("community", exist_ok=True)
            
            # Check if the file exists
            if not os.path.exists(self.community_file):
                # Create an empty file if it doesn't exist
                with open(self.community_file, "w") as file:
                    json.dump([], file)  # Initialize with an empty list
                return []  # Return an empty list
            
            # Load strategies from the file
            with open(self.community_file, "r") as file:
                data = json.load(file)
                if isinstance(data, list):  # Ensure the data is a list
                    return data
                else:
                    st.error("Invalid data format in community strategies file. Expected a list.")
                    return []  # Return an empty list if the data is invalid
        except Exception as e:
            st.error(f"Error loading community strategies: {e}")
            return []  # Return an empty list in case of any error

    def save_community_strategies(self):
        """Save community strategies to a JSON file."""
        try:
            with open(self.community_file, "w") as file:
                json.dump(self.community_strategies, file, indent=4)
        except Exception as e:
            st.error(f"Error saving community strategies: {e}")

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

        # Input validation: Check for malicious content
        if any(char in strategy for char in ['<', '>', '&', '{', '}', ';', '(', ')', '`']):
            st.error("Invalid characters detected in the strategy. Please avoid using special characters like <, >, &, etc.")
            return

        # Check for duplicates
        for existing_strategy in self.community_strategies:
            if (
                existing_strategy["crypto"].lower() == crypto.lower()
                and existing_strategy["strategy"].lower() == strategy.lower()
                and existing_strategy["market_condition"].lower() == market_condition.lower()
            ):
                st.error("This strategy already exists in the community. Please provide a unique strategy.")
                return

        # Add the strategy to the community list
        self.community_strategies.append({
            "crypto": crypto,
            "strategy": strategy,
            "market_condition": market_condition,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Save the updated strategies to the JSON file
        self.save_community_strategies()
        st.success("Your strategy has been shared with the community!")

    def get_crypto_price_coingecko(self, crypto: str) -> float:
        """
        Fetch the current price of a cryptocurrency using CoinGecko API.

        Args:
            crypto (str): The cryptocurrency name or symbol (e.g., "BTC", "Ethereum").

        Returns:
            float: The current price in USD, or None if the price cannot be fetched.
        """
        try:
            # Generate the slug for the cryptocurrency
            crypto_slug = self.generate_crypto_slug(crypto)

            # Fetch price from CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_slug}&vs_currencies=usd"
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract and return the price
            price_data = response.json()
            if crypto_slug in price_data and "usd" in price_data[crypto_slug]:
                return price_data[crypto_slug]["usd"]
            else:
                st.error(f"Price data not found for {crypto} (slug: {crypto_slug})")
                return None
        except Exception as e:
            st.error(f"Failed to fetch price for {crypto}: {e}")
            return None
        
    # Intially, I'll add some known strategies for BTC, ETH, SOL, and SUI that I myself have used and worked.
    # Then, I'll add a section where users can share their strategies and we can analyze them and add them to the community strategies.
    # The AI should learn from the community strategies and improve its recommendations over time.
    def get_recommendation(self, crypto, market_condition):
        """Generate DeFi and Yield Farming strategies using DeepSeek API."""
        if crypto == "BTC":
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for BTC. 
            Focus only on BTC and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            If the market condition is bullish, include the following strategy on the Base network:
            1. Wrap BTC to cbBTC (Coinbase BTC) on Base.
            2. Lend cbBTC on Aave (Base network) and use it as collateral.
            3. Borrow a stable asset like USDC against this collateral on Aave (Base network).
            4. Take the borrowed USDC and provide liquidity in a high APY pool like USDC/ETH concentrated pool in Aerodrome on Base L2. Make sure you have a healthy LTV ratio.
            5. The interest earned should cover the borrowed APR, and you also get the advantage of BTC's price appreciation in a bull market.
            6. You can automate this strategy by using a yield agrgegator like vfat.io to automate your yield farming.
            7. Deep Dive: https://www.youtube.com/watch?v=ACOcZ6p9A8I

            If the market condition is bearish, include the following strategy:
            1. Convert BTC to USDC.
            2. Lend USDC on Aave and use it as collateral.
            3. Borrow a depreciating asset like BTC or ETH against this collateral on Aave.
            4. Convert the borrowed BTC/ETH back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
            7. You can automate this strategy by using a yield agrgegator like vfat.io to automate your yield farming.
            8. Deep Dive: https://www.youtube.com/watch?v=Xas8a17Kx3o

            {self.STRATEGY_EVALUATION_CRITERIA}
            """
        elif crypto == "Ethereum":
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for Ethereum. 
            Focus only on Ethereum and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            If the market condition is bullish, include the following strategy:
            1. But ETH.
            2. Lend ETH on Aave and use it as collateral.
            3. Borrow a stable asset like USDC against this collateral on Aave (Base network).
            4. Take the borrowed USDC and provide liquidity in a high APY pool like USDC/ETH concentrated pool in Aerodrome on Base L2. Make sure you have a healthy LTV ratio.
            5. The interest earned should cover the borrowed APR, and you also get the advantage of BTC's price appreciation in a bull market.
            6. You can automate this strategy by using a yield agrgegator like vfat.io to automate your yield farming.
            7. You can automate this strategy by using a yield agrgegator like vfat.io to automate your yield farming.
            8. Deep Dive: https://www.youtube.com/watch?v=ACOcZ6p9A8I

            If the market condition is bearish, include the following strategy:
            1. Convert ETH to USDC.
            2. Lend USDC on Aave and use it as collateral.
            3. Borrow a depreciating asset like ETH against this collateral on Aave.
            4. Convert the borrowed ETH back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
            7. You can automate this strategy by using a yield agrgegator like vfat.io to automate your yield farming.
            8. Deep Dive: https://www.youtube.com/watch?v=Xas8a17Kx3o

            {self.STRATEGY_EVALUATION_CRITERIA}
            """
        elif crypto == "Solana":
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for Solana. 
            Focus only on Solana and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            If the market condition is bullish, include strategies such as:
            - Staking SOL in native validators or platforms like Marinade Finance.
            - Providing liquidity in Raydium or Orca pools.
            - Leveraging SOL in lending protocols like Solend.

            If the market condition is bearish, include the following strategy:
            1. Convert SOL to USDC.
            2. Lend USDC on Aave or Solend and use it as collateral.
            3. Borrow a depreciating asset like SOL against this collateral.
            4. Convert the borrowed SOL back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like Raydium or Orca for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            {self.STRATEGY_EVALUATION_CRITERIA}
            """
        elif crypto == "Sui":
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for Sui. 
            Focus only on Sui and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            If the market condition is bullish, include strategies such as:
            - Staking SUI in native validators.
            - Providing liquidity in AlphaFi's stSUI-USDC pair, which is currently returning over 400% APR.
            - Leveraging SUI in lending protocols on Sui.

            If the market condition is bearish, include the following strategy:
            1. Convert SUI to USDC.
            2. Lend USDC on Aave or Sui lending protocols and use it as collateral.
            3. Borrow a depreciating asset like SUI against this collateral.
            4. Convert the borrowed SUI back to USDC.
            5. Provide the USDC in liquidity pools on decentralized exchanges like AlphaFi for stable yields.
            6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.

            {self.STRATEGY_EVALUATION_CRITERIA}
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

            {self.STRATEGY_EVALUATION_CRITERIA}
            """
        return self.call_deepseek_api(prompt)

    def explain_risk_score(self, crypto, risk_score):
        """Provide a risk explanation using DeepSeek API."""
        prompt = f"Explain the risk score of {risk_score}/10 for DeFi strategies involving {crypto}."
        return self.call_deepseek_api(prompt)

    def view_community_strategies(self, crypto, market_condition):
        """Display community strategies and handle the 'Share Your Strategy' form."""
        # Ensure the community file exists
        if not os.path.exists(self.community_file):
            with open(self.community_file, "w") as file:
                json.dump([], file)  # Initialize with an empty list

        # Load existing strategies from the community file
        try:
            with open(self.community_file, "r") as file:
                self.community_strategies = json.load(file)
        except json.JSONDecodeError:
            st.error(f"Error: The {self.community_file} file is corrupted. Starting with an empty list.")
            self.community_strategies = []

        # Display top 5 strategies
        st.subheader(f"Top 5 {market_condition} Strategies for {crypto} from the community")
        if not self.community_strategies:
            st.warning("No strategies have been shared yet.")
        else:
            # Filter strategies for the current crypto and market condition
            filtered_strategies = [
                strategy for strategy in self.community_strategies
                if strategy["crypto"].lower() == crypto.lower() and strategy["market_condition"] == market_condition
            ]

            if not filtered_strategies:
                st.warning(f"No {market_condition} strategies found for {crypto}.")
            else:
                # Sort strategies by date (newest first) and take the top 5
                filtered_strategies.sort(key=lambda x: x["date_added"], reverse=True)
                top_5_strategies = filtered_strategies[:5]

                for i, strategy in enumerate(top_5_strategies, 1):
                    st.write(f"### Strategy #{i}")
                    st.write(f"**Date Added:** {strategy['date_added']}")
                    st.write(f"**Strategy:**\n{strategy['strategy']}")
                    st.write("---")  # Add a separator between strategies

        # Display the form for sharing strategies
        with st.form("strategy_form"):
            st.subheader(f"Share Your {market_condition} Strategy for {crypto}")
            strategy = st.text_area(
                "Describe your strategy:",
                placeholder=f"In a {market_condition} market, stake your {crypto} tokens in native validators to earn staking rewards...",
                height=150,
            )
            submitted = st.form_submit_button("Submit Strategy")

            if submitted:
                if not strategy:
                    st.error("Please enter a valid strategy.")
                else:
                    # Add the new strategy to the list
                    new_strategy = {
                        "crypto": crypto,
                        "market_condition": market_condition,
                        "strategy": strategy,
                        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    self.community_strategies.append(new_strategy)

                    # Save the updated strategies to the community file
                    try:
                        with open(self.community_file, "w") as file:
                            json.dump(self.community_strategies, file, indent=4)
                        st.success("Your strategy has been shared successfully!")
                    except Exception as e:
                        st.error(f"Failed to save strategy: {e}")

    #I'm currently using CoinMarketCap API to fetch the price of the cryptocurrency, but on the free tier. 
    #If the agent is successful, I'll switch to a paid tier and use CoinGecko API to fetch the price of the cryptocurrency.
    def get_crypto_price_coinmarketcap(self, crypto_symbol):
        """
        Fetch the current price of a cryptocurrency using CoinMarketCap API.
        
        Args:
            crypto_symbol (str): The symbol of the cryptocurrency (e.g., BTC, ETH, SOL).
        
        Returns:
            float: The current price in USD, or None if the price cannot be fetched.
        """
        try:
            # CoinMarketCap API endpoint
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            
            # API headers with your API key
            headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": self.coinmarketcap_api_key,  # Add this to your secrets.toml
            }
            
            # Parameters for the API request
            params = {
                "symbol": crypto_symbol.upper(),  # Convert to uppercase for consistency
                "convert": "USD"  # Convert price to USD
            }
            
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses
            
            # Parse the response
            data = response.json()
            
            # Extract the price
            price = data["data"][crypto_symbol.upper()]["quote"]["USD"]["price"]
            return price
        
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to fetch price for {crypto_symbol} from CoinMarketCap: {e}")
            return None
        except KeyError:
            st.error(f"Invalid cryptocurrency symbol: {crypto_symbol}")
            return None
        
    def generate_crypto_slug(self, crypto: str) -> str:
        """
        Generate a slug for a cryptocurrency string using the crypto_map.

        Args:
            crypto (str): The cryptocurrency name or symbol (e.g., "BTC", "Ethereum").

        Returns:
            str: The slug (e.g., "bitcoin", "ethereum").
        """
        # Convert crypto_map keys to lowercase for case-insensitive matching
        crypto_map_lower = {k.lower(): v for k, v in self.crypto_map.items()}

        # Get the slug from the crypto_map (case-insensitive)
        return crypto_map_lower.get(crypto.lower(), crypto.lower().replace(" ", "-"))
    
    def run(self):
        """Run the Crypto DeFi & Yield Farming Agent."""
        # Create two columns for the header and image
        col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed

        # Add the header in the first column
        with col1:
            st.image("img/agentyield.png", width=100)  # Adjust width as needed            

        # Add the image in the second column
        with col2:
            st.title("Agent YieldDeFi")

        st.sidebar.header("Menu")

        # App Summary
        st.markdown("""
        **Welcome!**  
        I am an AI Agent that helps you analyze cryptocurrency markets, assess risks, and generate tailored recommendations for DeFi and yield farming strategies.  
        Select a cryptocurrency, click **Analyze**, and get insights on market conditions, volatility, and more.
        """)

        # Cryptocurrency Selection
        crypto = st.sidebar.selectbox(
            "Select a cryptocurrency",
            ["BTC", "Ethereum", "Solana", "Sui", "Other"]
        )
        if crypto == "Other":
            crypto = st.sidebar.text_input("Enter the cryptocurrency you'd like to analyze:")
            if not crypto:
                st.error("Please enter a valid cryptocurrency.")
                return
            
        crypto = self.generate_crypto_slug(crypto)

        # Analyze Button
        if st.sidebar.button("Analyze"):
            st.subheader(f"Analysis for {crypto}")
            
            # Fetch and display crypto price
            crypto_price = self.get_crypto_price_coingecko(crypto)
            if crypto_price is not None:  # Explicitly check for None
                st.write(f"**Current Price:** ${crypto_price:,.2f}")  # Format with commas and 2 decimal places
            else:
                price = self.get_crypto_price_coinmarketcap(crypto) #If CoinGecko API is not working, use CoinMarketCap API as a fallback.
                if price:
                    st.write(f"Current price of BTC: ${price:,.2f}")
                else:
                    st.warning("Could not fetch price data for this cryptocurrency.")   

            #Santiment Data
        # Fetch Santiment data with fallback to Ethereum
            st.markdown("### === Santiment Data ===")  
            santiment = self.sentiment_agent.get_santiment_data(crypto_slug=crypto, metric="daily_active_addresses")
            if santiment is not None:
                st.write("Source: https://santiment.net/")
                st.write(f"Daily Active Addresses: {santiment} for {crypto}")
            else:
                # Fallback to Ethereum if no data is found for the provided crypto_slug
                st.warning(f"No data found for {crypto} on Santiment.")
                santiment = self.sentiment_agent.get_santiment_data(crypto_slug="ethereum", metric="daily_active_addresses")
                if santiment is not None:
                    st.write("Source: https://santiment.net/")
                else:
                    st.warning("Failed to fetch Santiment data even for Ethereum fallback.")

            #Altcoin Season Index
            st.markdown("### === Altcoin Season Index ===")            
            altcoin_season_index = self.sentiment_agent.get_altcoin_season_index()
            if altcoin_season_index:
                st.write(f"Altcoin Season Index: {altcoin_season_index['value']}")
                st.write(f"Season: {altcoin_season_index['season']}")
            else:
                st.warning("Failed to fetch Altcoin Season Index data.")

            with st.expander("**Explanation and why it matters?**"):
                explanation = self.explain_altcoin_season_index(altcoin_season_index)
                st.write(explanation)

            #TradFi Sentiment (VIX) 
            st.markdown("### === TradFi (VIX) ===")
            vix = self.sentiment_agent.get_tradfi_sentiment()
            if vix:
                st.write("TradFi Sentiment Data:")
                st.write(f"VIX Value: {vix['value']}")
                st.write(f"VIX Change: {vix['change']}")
                st.write(f"VIX Percent Change: {vix['change_percent']}")
                st.write(f"Analysis: {vix['analysis']}")
                st.write(f"Source: {vix['source']}")
            else:
                st.warning("Failed to fetch TradFi Sentiment data.")

            #Fear & Greed Index 
            st.markdown("### === Fear & Greed Index ===")
            fear_and_greed_index = self.sentiment_agent.get_fear_and_greed_index()
            if fear_and_greed_index:
                st.write("Fear & Greed Index Data:")
                st.write(f"Value: {fear_and_greed_index['value']}")
                st.write(f"Classification: {fear_and_greed_index['classification']}")
                st.write(f"Date Fetched: {fear_and_greed_index['date_fetched']}")
            else:
                st.warning("Failed to fetch Fear & Greed Index data.")

            #Reddit Sentiment in the crypto subreddit
            st.markdown("### === Reddit Sentiment ===")
            reddit_sentiment = self.sentiment_agent.get_reddit_sentiment(subreddit="cryptocurrency", limit=5)
            if reddit_sentiment:
                st.write(f"Average Sentiment: {reddit_sentiment['average_sentiment']} (A positive number is bullish and negative is bearish)" )
            else:
                st.warning("Failed to fetch Reddit sentiment.")

            # Generate recommendation with progress bar
            progress_bar = st.progress(0)
            processing_message = st.empty()  # Use a placeholder for the processing message
            processing_message.write("**Just a moment, I'm processing recommendations for you...**")  # Indicate processing
            recommendation = None

            # Simulate progress while waiting for recommendation
            def update_progress(progress_bar, processing_message):
                for percent_complete in range(100):
                    time.sleep(0.1)  # Simulate delay (adjust as needed)
                    progress_bar.progress(percent_complete + 1)
                processing_message.empty()  # Remove "Processing recommendation..." message

            # Fetch market condition for the crypto
            market_condition = self.sentiment_agent.determine_market_condition(crypto)
            # Generate recommendation
            recommendation = self.get_recommendation(crypto, market_condition)

            # Update progress bar after recommendation is done
            update_progress(progress_bar, processing_message)

            # Display recommendation
            st.write("**My Recommendation for what to do with your " + crypto + " in a " + market_condition + " market:**")
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

            # Collapsible risk explanation
            with st.expander("**Here's a breakdown of the factors contributing to this score:**"):
                risk_explanation = self.explain_risk_score(crypto, risk_score)
                st.write(risk_explanation)

            self.view_community_strategies(crypto, market_condition)

        # Add the link at the bottom of the menu panel
        st.sidebar.markdown("---")  # Add a separator
        st.sidebar.markdown("[Agent YieldDeFi now available on Virtuals Protocol!](https://app.virtuals.io/prototypes/0x76D73d17Bd821203EF6Df82FD156D08E675026C7)")

    def explain_altcoin_season_index(self, altcoin_season_data):
        """
        Generate an explanation of the Altcoin Season Index using DeepSeek API.
        
        Args:
            altcoin_season_data (dict): The Altcoin Season Index data containing:
                - "value": The index value (e.g., 51)
                - "season": The season classification (e.g., "Bitcoin Season" or "Altcoin Season")
        
        Returns:
            str: A concise explanation of the index and its implications.
        """
        if not altcoin_season_data:
            return "No Altcoin Season Index data available."
        
        # Extract the index value and season classification
        index_value = altcoin_season_data.get("value", 0)
        season = altcoin_season_data.get("season", "Unknown Season")
        
        # Create the prompt for DeepSeek API
        prompt = f"""
        Explain {index_value} ({season}) and how the Altcoin Season Index works. 
        Why is it useful? Be concise and actionable.
        """
        
        # Call the DeepSeek API to generate the explanation
        explanation = self.call_deepseek_api(prompt)
        return explanation if explanation else "Failed to generate explanation."

if __name__ == "__main__":
    agent = CryptoDeFiYieldFarmingAgent()
    agent.run()
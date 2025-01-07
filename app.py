import streamlit as st
import datetime
import json
import requests
from dotenv import load_dotenv
import os
from sentiment import Sentiment

# Load environment variables from .env
load_dotenv()

# Constants
COMMUNITY_FILE = "community/community_strategies.json"
CRYPTO_MAP = {
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
    "Synthetix": "synthetix-network-token",
    "Ren": "ren",
    "Reserve Rights": "reserve-rights-token",
}

# Initialize Sentiment class
@st.cache_resource
def get_sentiment_agent():
    return Sentiment()

# Initialize and run the app
@st.cache_resource
def get_crypto_app():
    return CryptoDeFiYieldFarmingAgent()

class CryptoDeFiYieldFarmingAgent:
    def __init__(self):
        self.STRATEGY_EVALUATION_CRITERIA = """
        Be concise, actionable, provide pros and cons, and a rating (1-10) of what you think for each strategy. 
        Include a link to a website or a YouTube video explaining the strategy. 
        Do not include deep dives if it's irrelevant, not helpful, or missing content.
        """
        self.community_strategies = self._load_community_strategies()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL")
        self.coinmarketcap_api_key = os.getenv("COINMARKETCAP_API_KEY")
        self.sentiment_agent = get_sentiment_agent()

    def _load_community_strategies(self):
        """Load community strategies from a JSON file."""
        try:
            os.makedirs("community", exist_ok=True)
            if not os.path.exists(COMMUNITY_FILE):
                with open(COMMUNITY_FILE, "w") as file:
                    json.dump([], file)
                return []

            with open(COMMUNITY_FILE, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                else:
                    st.error("Invalid data format in community strategies file. Expected a list.")
                    return []
        except Exception as e:
            st.error(f"Error loading community strategies: {e}")
            return []

    def _save_community_strategies(self):
        """Save community strategies to a JSON file."""
        try:
            with open(COMMUNITY_FILE, "w") as file:
                json.dump(self.community_strategies, file, indent=4)
        except Exception as e:
            st.error(f"Error saving community strategies: {e}")

    def call_deepseek_api(self, prompt):
        """Call the DeepSeek API to generate insights or analyze data."""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a Crypto Finance Analyst specializing in DeFi and Yield Farming."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        response = requests.post(
            f"{self.deepseek_api_url}/chat/completions",
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

        if any(char in strategy for char in ['<', '>', '&', '{', '}', ';', '(', ')', '`']):
            st.error("Invalid characters detected in the strategy. Please avoid using special characters.")
            return

        for existing_strategy in self.community_strategies:
            if (
                existing_strategy["crypto"].lower() == crypto.lower()
                and existing_strategy["strategy"].lower() == strategy.lower()
                and existing_strategy["market_condition"].lower() == market_condition.lower()
            ):
                st.error("This strategy already exists in the community. Please provide a unique strategy.")
                return

        self.community_strategies.append({
            "crypto": crypto,
            "strategy": strategy,
            "market_condition": market_condition,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        self._save_community_strategies()
        st.success("Your strategy has been shared with the community!")

    def get_crypto_price_coingecko(self, crypto: str) -> float:
        """Fetch the current price of a cryptocurrency using CoinGecko API."""
        try:
            crypto_slug = CRYPTO_MAP.get(crypto.lower(), crypto.lower())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_slug}&vs_currencies=usd"
            response = requests.get(url)
            response.raise_for_status()

            price_data = response.json()
            if crypto_slug in price_data and "usd" in price_data[crypto_slug]:
                return price_data[crypto_slug]["usd"]
            else:
                st.error(f"Price data not found for {crypto} (slug: {crypto_slug})")
                return None
        except Exception as e:
            st.error(f"Failed to fetch price for {crypto}: {e}")
            return None
        
    def get_recommendation(self, crypto, market_condition):
        """Generate DeFi and Yield Farming strategies using DeepSeek API."""
        # Define strategies for each cryptocurrency and market condition
        strategies = {
            "BTC": {
                "bullish": """
                1. Wrap BTC to cbBTC (Coinbase BTC) on Base.
                2. Lend cbBTC on Aave (Base network) and use it as collateral.
                3. Borrow a stable asset like USDC against this collateral on Aave (Base network).
                4. Take the borrowed USDC and provide liquidity in a high APY pool like USDC/ETH concentrated pool in Aerodrome on Base L2. Make sure you have a healthy LTV ratio.
                5. The interest earned should cover the borrowed APR, and you also get the advantage of BTC's price appreciation in a bull market.
                6. You can automate this strategy by using a yield aggregator like vfat.io to automate your yield farming.
                7. Deep Dive: https://www.youtube.com/watch?v=ACOcZ6p9A8I
                """,
                "bearish": """
                1. Convert BTC to USDC.
                2. Lend USDC on Aave and use it as collateral.
                3. Borrow a depreciating asset like BTC or ETH against this collateral on Aave.
                4. Convert the borrowed BTC/ETH back to USDC.
                5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
                6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
                7. You can automate this strategy by using a yield aggregator like vfat.io to automate your yield farming.
                8. Deep Dive: https://www.youtube.com/watch?v=Xas8a17Kx3o
                """
            },
            "Ethereum": {
                "bullish": """
                1. Buy ETH.
                2. Lend ETH on Aave and use it as collateral.
                3. Borrow a stable asset like USDC against this collateral on Aave (Base network).
                4. Take the borrowed USDC and provide liquidity in a high APY pool like USDC/ETH concentrated pool in Aerodrome on Base L2. Make sure you have a healthy LTV ratio.
                5. The interest earned should cover the borrowed APR, and you also get the advantage of ETH's price appreciation in a bull market.
                6. You can automate this strategy by using a yield aggregator like vfat.io to automate your yield farming.
                7. Deep Dive: https://www.youtube.com/watch?v=ACOcZ6p9A8I
                """,
                "bearish": """
                1. Convert ETH to USDC.
                2. Lend USDC on Aave and use it as collateral.
                3. Borrow a depreciating asset like ETH against this collateral on Aave.
                4. Convert the borrowed ETH back to USDC.
                5. Provide the USDC in liquidity pools on decentralized exchanges like Aerodrome for stable yields.
                6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
                7. You can automate this strategy by using a yield aggregator like vfat.io to automate your yield farming.
                8. Deep Dive: https://www.youtube.com/watch?v=Xas8a17Kx3o
                """
            },
            "Solana": {
                "bullish": """
                - Staking SOL in native validators or platforms like Marinade Finance.
                - Providing liquidity in Raydium or Orca pools.
                - Leveraging SOL in lending protocols like Solend.
                """,
                "bearish": """
                1. Convert SOL to USDC.
                2. Lend USDC on Aave or Solend and use it as collateral.
                3. Borrow a depreciating asset like SOL against this collateral.
                4. Convert the borrowed SOL back to USDC.
                5. Provide the USDC in liquidity pools on decentralized exchanges like Raydium or Orca for stable yields.
                6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
                """
            },
            "Sui": {
                "bullish": """
                - Staking SUI in native validators.
                - Providing liquidity in AlphaFi's stSUI-USDC pair, which is currently returning over 400% APR.
                - Leveraging SUI in lending protocols on Sui.
                """,
                "bearish": """
                1. Convert SUI to USDC.
                2. Lend USDC on Aave or Sui lending protocols and use it as collateral.
                3. Borrow a depreciating asset like SUI against this collateral.
                4. Convert the borrowed SUI back to USDC.
                5. Provide the USDC in liquidity pools on decentralized exchanges like AlphaFi for stable yields.
                6. The interest earned should cover the borrowing costs, and you benefit from the depreciating value of the borrowed asset.
                """
            }
        }

        # Generate the prompt based on the cryptocurrency and market condition
        if crypto in strategies:
            prompt = f"""
            Provide a {market_condition} DeFi/Yield Farming strategy for {crypto}. 
            Focus only on {crypto} and provide multiple strategies tailored to it.
            Do not include strategies for other cryptocurrencies or for market conditions other than {market_condition}.

            {strategies[crypto][market_condition.lower()]}

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
        if not os.path.exists(COMMUNITY_FILE):
            with open(COMMUNITY_FILE, "w") as file:
                json.dump([], file)

        # Load existing strategies from the community file
        try:
            with open(COMMUNITY_FILE, "r") as file:
                self.community_strategies = json.load(file)
        except json.JSONDecodeError:
            st.error(f"Error: The {COMMUNITY_FILE} file is corrupted. Starting with an empty list.")
            self.community_strategies = []

        # Initialize session state for selected strategy index and analysis result
        if "selected_strategy_index" not in st.session_state:
            st.session_state.selected_strategy_index = None
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None

        # Initialize debug logs in session state
        #if "debug_logs" not in st.session_state:
            #st.session_state.debug_logs = []

        # Cache the filtered strategies to avoid recomputation on every reload
        @st.cache_data
        def get_filtered_strategies(community_strategies, crypto, market_condition):
            return [
                strategy for strategy in community_strategies
                if strategy["crypto"].lower() == crypto.lower() and strategy["market_condition"] == market_condition
            ]

        # Display top 5 strategies
        st.subheader(f"Top 5 {market_condition} Strategies for {crypto} from the community")
        if not self.community_strategies:
            st.warning("No strategies have been shared yet.")
        else:
            # Filter strategies for the current crypto and market condition
            filtered_strategies = get_filtered_strategies(self.community_strategies, crypto, market_condition)

            if not filtered_strategies:
                st.warning(f"No {market_condition} strategies found for {crypto}.")
            else:
                # Sort strategies by date (newest first) and take the top 5
                filtered_strategies.sort(key=lambda x: x["date_added"], reverse=True)
                top_5_strategies = filtered_strategies[:5]

                # Display strategies
                for i, strategy in enumerate(top_5_strategies, 1):
                    st.write(f"### Strategy #{i}")
                    st.write(f"**Date Added:** {strategy['date_added']}")
                    st.write(f"**Strategy:**\n{strategy['strategy']}")
                    st.write("---")  # Add a separator between strategies

                # Create a form for strategy selection
                with st.form("strategy_selection_form"):
                    # Display strategies with a selection option
                    strategy_options = [f"Strategy #{i}" for i in range(1, len(top_5_strategies) + 1)]
                    selected_strategy = st.selectbox(
                        "Select a community strategy to analyze:",
                        strategy_options,
                        index=0,
                        key="strategy_selectbox"
                    )

                    # Add form submit button
                    submit_button = st.form_submit_button("Analyze Selected Strategy")

                    # Handle form submission
                    if submit_button:
                        st.session_state.debug_logs.append(f"Submit button clicked! Selected strategy: {selected_strategy}")  # Debug message 1

                        if selected_strategy and "#" in selected_strategy:
                            st.session_state.debug_logs.append(f"Valid strategy selected: {selected_strategy}")  # Debug message 2

                            selected_index = int(selected_strategy.split("#")[1]) - 1
                            selected_strategy_data = top_5_strategies[selected_index]

                            # Store the selected strategy in session state
                            st.session_state.selected_strategy = selected_strategy_data
                            st.session_state.debug_logs.append(f"Selected strategy stored in session state: {st.session_state.selected_strategy}")  # Debug message 3

                            # Use query parameters to navigate to the analysis page
                            st.query_params.update(
                                page="community_analysis",
                                crypto=crypto,
                                market_condition=market_condition,
                                strategy_index=selected_index
                            )
                            st.session_state.debug_logs.append(f"Query parameters updated: {st.query_params}")  # Debug message 4

                            # Set a flag to indicate navigation is needed
                            st.session_state.should_navigate = True
                            st.session_state.debug_logs.append(f"Navigation flag set to: {st.session_state.should_navigate}")  # Debug message 5
                        else:
                            st.session_state.debug_logs.append(f"No valid strategy selected. Selected strategy: {selected_strategy}")  # Debug message 6

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
                        "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    self.community_strategies.append(new_strategy)

                    # Save the updated strategies to the community file
                    try:
                        with open(COMMUNITY_FILE, "w") as file:
                            json.dump(self.community_strategies, file, indent=4)
                        st.success("Your strategy has been shared successfully!")
                    except Exception as e:
                        st.error(f"Failed to save strategy: {e}")

    def get_crypto_price_coinmarketcap(self, crypto_symbol):
        """
        Fetch the current price of a cryptocurrency using CoinMarketCap API.
        
        Args:
            crypto_symbol (str): The symbol of the cryptocurrency (e.g., BTC, ETH, SOL).
        
        Returns:
            float: The current price in USD, or None if the price cannot be fetched.
        """
        try:
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": self.coinmarketcap_api_key,
            }
            params = {
                "symbol": crypto_symbol.upper(),
                "convert": "USD"
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
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
        crypto_map_lower = {k.lower(): v for k, v in CRYPTO_MAP.items()}
        return crypto_map_lower.get(crypto.lower(), crypto.lower().replace(" ", "-"))
    
    def run(self):
        """Run the Crypto DeFi & Yield Farming Agent."""
        # Display header with logo and title
        self._display_header()

        # Display app summary
        self._display_app_summary()

        # Sidebar menu
        crypto = self._display_sidebar_menu()

        # Analyze button logic
        if st.sidebar.button("Analyze"):
            self._analyze_crypto(crypto)

        # Add the link at the bottom of the menu panel
        st.sidebar.markdown("---")  # Add a separator
        st.sidebar.markdown("[Agent YieldDeFi now available on Virtuals Protocol!](https://app.virtuals.io/prototypes/0x76D73d17Bd821203EF6Df82FD156D08E675026C7)")

        # Footer with links
        st.markdown(
            """
            ---
            **Explore More:**  
            - [ 👉 Agent YieldDefi Documentation](https://agent-yielddefi.gitbook.io/agent-yielddefi-docs)  
            - [ 👉 Virtuals.io Prototype](https://app.virtuals.io/prototypes/0x76D73d17Bd821203EF6Df82FD156D08E675026C7)  
            - [ 👉 Project Roadmap](https://github.com/AdonisVillanueva/crypto-defi-yield-farming-agent/blob/main/ROADMAP.md)  
            """
        )

    def _display_header(self):
        """Display the header with logo and title."""
        col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed
        with col1:
            st.image("img/agentyield.png", width=100)  # Adjust width as needed
        with col2:
            st.title("Agent YieldDeFi")

    def _display_app_summary(self):
        """Display the app summary."""
        st.markdown("""
        **Welcome!**  
        I am an AI Agent that helps you analyze cryptocurrency markets, assess risks, and generate tailored recommendations for DeFi and yield farming strategies.  
        Select a cryptocurrency, click **Analyze**, and get insights on market conditions, volatility, and more.
        """)

    def _display_sidebar_menu(self):
        """Display the sidebar menu and return the selected cryptocurrency."""
        st.sidebar.header("Menu")
        crypto = st.sidebar.selectbox(
            "Select a cryptocurrency",
            ["BTC", "Ethereum", "Solana", "Sui", "Other"]
        )
        if crypto == "Other":
            crypto = st.sidebar.text_input("Enter the cryptocurrency you'd like to analyze:")
            if not crypto:
                st.error("Please enter a valid cryptocurrency.")
                return None
        return self.generate_crypto_slug(crypto)

    def _analyze_crypto(self, crypto):
        """Analyze the selected cryptocurrency and display results."""
        st.subheader(f"Analysis for {crypto}")

        # Fetch and display crypto price
        self._display_crypto_price(crypto)

        # Fetch and display Santiment data
        self._display_santiment_data(crypto)

        # Fetch and display Altcoin Season Index
        self._display_altcoin_season_index()

        # Fetch and display TradFi Sentiment (VIX)
        self._display_tradfi_sentiment()

        # Fetch and display Fear & Greed Index
        self._display_fear_and_greed_index()

        # Fetch and display Reddit Sentiment
        self._display_reddit_sentiment()

        # Generate recommendation with a spinner
        with st.spinner("**Just a moment while I'm processing recommendations for you...**"):
            market_condition = self.sentiment_agent.determine_market_condition(crypto)
            recommendation = self.get_recommendation(crypto, market_condition)

        # Display recommendation
        st.write("**My Recommendation for what to do with your " + crypto + " in a " + market_condition + " market:**")
        st.markdown(recommendation.replace("\n", "  \n"))

        # Display risk score with red line and indicator
        risk_score = 5  # Example risk score (you can calculate this dynamically)
        self._display_risk_score(risk_score)

        # Analyze risk factors and display community strategies
        with st.spinner("**Analyzing the risk factors contributing to this score...**"):
            with st.expander("**Here's a breakdown of the factors contributing to this score:**"):
                risk_explanation = self.explain_risk_score(crypto, risk_score)
                st.write(risk_explanation)
            #self.view_community_strategies(crypto, market_condition)

    def _display_crypto_price(self, crypto):
        """Fetch and display the current price of the cryptocurrency."""
        crypto_price = self.get_crypto_price_coingecko(crypto)
        if crypto_price is not None:
            st.write(f"**Current Price:** ${crypto_price:,.2f}")  # Format with commas and 2 decimal places
        else:
            price = self.get_crypto_price_coinmarketcap(crypto)  # Fallback to CoinMarketCap API
            if price:
                st.write(f"Current price of {crypto}: ${price:,.2f}")
            else:
                st.warning("Could not fetch price data for this cryptocurrency.")

    def _display_santiment_data(self, crypto):
        """Fetch and display Santiment data."""
        st.markdown("### === Santiment Data ===")
        santiment = self.sentiment_agent.get_santiment_data(crypto_slug=crypto, metric="daily_active_addresses")
        if santiment is not None:
            st.write("Source: https://santiment.net/")
            st.write(f"Daily Active Addresses: {santiment} for {crypto}")
        else:
            st.warning(f"No data found for {crypto} on Santiment.")
            santiment = self.sentiment_agent.get_santiment_data(crypto_slug="ethereum", metric="daily_active_addresses")
            if santiment is not None:
                st.write("Source: https://santiment.net/")
            else:
                st.warning("Failed to fetch Santiment data even for Ethereum fallback.")

    def _display_altcoin_season_index(self):
        """Fetch and display Altcoin Season Index."""
        st.markdown("### === Altcoin Season Index ===")
        altcoin_season_index = self.sentiment_agent.get_altcoin_season_index()
        if altcoin_season_index:
            st.write(f"Altcoin Season Index: {altcoin_season_index['value']}")
            st.write(f"Season: {altcoin_season_index['season']}")
            with st.expander("**Explanation and why it matters?**"):
                explanation = self.explain_altcoin_season_index(altcoin_season_index)
                st.write(explanation)
        else:
            st.warning("Failed to fetch Altcoin Season Index data.")

    def _display_tradfi_sentiment(self):
        """Fetch and display TradFi Sentiment (VIX)."""
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

    def _display_fear_and_greed_index(self):
        """Fetch and display Fear & Greed Index."""
        st.markdown("### === Fear & Greed Index ===")
        fear_and_greed_index = self.sentiment_agent.get_fear_and_greed_index()
        if fear_and_greed_index:
            st.write("Fear & Greed Index Data:")
            st.write(f"Value: {fear_and_greed_index['value']}")
            st.write(f"Classification: {fear_and_greed_index['classification']}")
            st.write(f"Date Fetched: {fear_and_greed_index['date_fetched']}")
        else:
            st.warning("Failed to fetch Fear & Greed Index data.")

    def _display_reddit_sentiment(self):
        """Fetch and display Reddit Sentiment."""
        st.markdown("### === Reddit Sentiment ===")
        reddit_sentiment = self.sentiment_agent.get_reddit_sentiment(subreddit="cryptocurrency", limit=5)
        if reddit_sentiment:
            st.write(f"Average Sentiment: {reddit_sentiment['average_sentiment']} (A positive number is bullish and negative is bearish)")
        else:
            st.warning("Failed to fetch Reddit sentiment.")

    def _display_risk_score(self, risk_score):
        """Display the risk score with a visual indicator."""
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

# if "debug_logs" not in st.session_state:
#     st.session_state.debug_logs = []

# # Display debug logs outside the form
# st.write("### Debug Logs")
# if st.session_state.debug_logs:
#     for log in st.session_state.debug_logs:
#         st.write(log)
# else:
#     st.write("No debug logs available.")  # Fallback message

# Handle navigation at the very end of the script
if st.session_state.get("should_navigate", False):
    st.switch_page("pages/community_analysis")

if __name__ == "__main__":
    agent = CryptoDeFiYieldFarmingAgent()
    agent.run()
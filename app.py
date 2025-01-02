import streamlit as st
import datetime
import json
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class CryptoDeFiYieldFarmingAgent:
    def __init__(self):
        self.community_file = "community_strategies.json"
        self.community_strategies = self.load_community_strategies()
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")  # Get API key from .env
        self.deepseek_api_url = "https://api.deepseek.com"  # Example endpoint

    def load_community_strategies(self):
        """Load community strategies from a JSON file."""
        try:
            with open(self.community_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

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
                {"role": "system", "content": "You are a helpful assistant."},
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

    def analyze_market(self):
        """Analyze the market condition using DeepSeek API."""
        prompt = "Analyze the current cryptocurrency market and determine if it's Altcoin Season or a Neutral Market."
        return self.call_deepseek_api(prompt)

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

    def view_community_strategies(self):
        """Display DeFi and yield farming strategies shared by the community."""
        if not self.community_strategies:
            st.warning("No strategies have been shared yet.")
            return

        st.subheader("Community DeFi Strategies")
        for i, strategy in enumerate(self.community_strategies, 1):
            st.write(f"**Strategy #{i}**")
            st.write(f"**Cryptocurrency:** {strategy['crypto']}")
            st.write(f"**Timestamp:** {strategy['timestamp']}")
            st.write(f"**Strategy:**\n{strategy['strategy']}")
            st.write("---")

    def run(self):
        """Run the Crypto DeFi & Yield Farming Agent."""
        st.title("Crypto DeFi & Yield Farming Agent")
        st.sidebar.header("Menu")
        crypto = st.sidebar.selectbox(
            "Select a cryptocurrency",
            ["BTC", "Ethereum", "Solana", "Sui", "Custom"]
        )
        if crypto == "Custom":
            crypto = st.sidebar.text_input("Enter the cryptocurrency you'd like to analyze:")

        if st.sidebar.button("Analyze"):
            st.subheader(f"Analysis for {crypto}")
            market_condition = self.analyze_market()
            st.write(f"**Market Condition:** {market_condition}")
            recommendation = self.get_recommendation(crypto, market_condition)
            st.write(f"**Recommendation:**\n{recommendation}")

            # Post-recommendation options
            st.subheader("Next Steps")
            if st.button("View Community Strategies"):
                self.view_community_strategies()
            if st.button("Share Your Strategy"):
                personal_strategy = st.text_area("Enter your personal strategy:")
                if st.button("Submit"):
                    self.community_strategies.append({
                        "crypto": crypto,
                        "strategy": personal_strategy,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    self.save_community_strategies()
                    st.success("Your strategy has been shared with the community!")

if __name__ == "__main__":
    agent = CryptoDeFiYieldFarmingAgent()
    agent.run()

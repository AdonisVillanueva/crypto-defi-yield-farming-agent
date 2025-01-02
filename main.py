import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import csv
from fpdf import FPDF
import json
import datetime
import re

class CryptoFinanceAgent:
    def __init__(self):
        load_dotenv()
        self.fear_greed_url = "https://api.alternative.me/fng/"
        self.vix_url = "https://finance.yahoo.com/quote/%5EVIX/"
        self.altcoin_season_url = "https://www.blockchaincenter.net/en/altcoin-season-index/"
        self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        self.community_file = "community/community_strategies.json"
        self.community_strategies = self.load_community_strategies()
    
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
            print(f"Error fetching Fear & Greed Index: {e}")
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
            print(f"Error fetching VIX Index: {e}")
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

    def get_vix_analysis(self, vix_value):
        """Analyze VIX value."""
        if vix_value >= 30:
            return "High Volatility (Market Fear)"
        elif vix_value >= 20:
            return "Moderate Volatility (Market Caution)"
        else:
            return "Low Volatility (Market Complacency)"

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
            'vix': vix_data,
            'altcoin_season': altcoin_season_data,
            'market_condition': market_condition
        }
    
    def get_crypto_price(self, crypto):
        """Fetch the current price of a cryptocurrency using CoinGecko API."""
        # Map cryptocurrency names to CoinGecko IDs
        crypto_id_map = {
            "BTC": "bitcoin",
            "Ethereum": "ethereum",
            "Solana": "solana",
            "Sui": "sui",
            # Add more mappings as needed
        }

        # Convert user input to CoinGecko ID
        crypto_id = crypto_id_map.get(crypto, crypto.lower())

        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()
            return data[crypto_id]["usd"]
        except Exception as e:
            print(f"Error fetching price for {crypto}: {e}")
            return None
        
    def get_recommendation(self, crypto, market_condition):
        """Generate DeFi and Yield Farming strategies using Deepseek API."""
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
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a Crypto Finance Analyst specializing in DeFi and Yield Farming."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return None

    def display_menu(self):
        """Display the main menu."""
        print("Would you like me to recommend a strategy for:")
        print("1. BTC")
        print("2. Ethereum")
        print("3. Solana")
        print("4. Sui")
        print("5. Any other crypto (I may not be fully trained for, YMMV)")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")
        return choice

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
            json.dump(self.community_strategies, file, indent=4)

    def is_valid_strategy(self, strategy):
        """Validate the strategy input to prevent malicious content."""
        # Allow letters, numbers, spaces, and common punctuation
        return bool(re.match(r"^[a-zA-Z0-9\s.,!?()\-']+$", strategy))

    def is_duplicate_strategy(self, crypto, strategy):
        """Check if the strategy already exists in the community file."""
        for entry in self.community_strategies:
            if entry["crypto"].lower() == crypto.lower() and entry["strategy"].lower() == strategy.lower():
                return True
        return False

    def share_strategy(self, crypto, strategy):
        """Allow users to share their strategy with the community."""
        if not self.is_valid_strategy(strategy):
            print("Invalid strategy. Please avoid special characters or scripts.")
            return
        if self.is_duplicate_strategy(crypto, strategy):
            print("This strategy already exists in the community.")
            return

        self.community_strategies.append({
            "crypto": crypto,
            "strategy": strategy,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_community_strategies()
        print("Your strategy has been shared with the community!")

    def view_community_strategies(self):
        """Display strategies shared by the community, including risk analysis."""
        if not self.community_strategies:
            print("No strategies have been shared yet.")
            return

        print("\n=== Community Strategies ===")
        for i, strategy in enumerate(self.community_strategies, 1):
            print(f"\nStrategy #{i}")
            print(f"Cryptocurrency: {strategy['crypto']}")
            print(f"Timestamp: {strategy['timestamp']}")
            print(f"Strategy:\n{strategy['strategy']}")
            # Analyze and display risks for the strategy
            risk_analysis = self.analyze_strategy_risks(strategy["crypto"], strategy["strategy"])
            print(f"\n{risk_analysis}")
        print("=" * 30 + "\n")

    def run(self):
        """Run the Crypto Finance Agent."""
        while True:
            choice = self.display_menu()
            if choice == "1":
                crypto = "BTC"
            elif choice == "2":
                crypto = "Ethereum"
            elif choice == "3":
                crypto = "Solana"
            elif choice == "4":
                crypto = "Sui"
            elif choice == "5":
                crypto = input("Enter the cryptocurrency you'd like to analyze: ")
            elif choice == "6":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
                continue

            # Fetch and display the crypto price
            price = self.get_crypto_price(crypto)
            if price:
                print(f"\nCurrent price of {crypto}: ${price}\n")

            market_condition = self.analyze_market()
            recommendation = self.get_recommendation(crypto, market_condition)
            if recommendation:
                print(f"\n=== Recommendation for {crypto} ===\n")
                print(recommendation)
                # Calculate and display risk score
                risk_score = self.calculate_risk_score(crypto, recommendation)
                print(f"\nRisk Score: {risk_score}/10")
                print(f"\nWhat does this mean?\n{self.explain_risk_score(crypto, risk_score)}")

                # Post-recommendation options
                while True:
                    print("\nWhat would you like to do next?")
                    print("1. Export these strategies (PDF/CSV)")
                    print("2. View community strategies")
                    print("3. Share your personal strategy")
                    print("4. Return to main menu")
                    post_choice = input("Enter your choice (1-4): ")

                    if post_choice == "1":
                        file_format = input("Export as PDF or CSV? ").upper()
                        if file_format in ["PDF", "CSV"]:
                            self.export_strategy(crypto, recommendation, file_format)
                        else:
                            print("Invalid file format. Export canceled.")
                    elif post_choice == "2":
                        self.view_community_strategies()
                    elif post_choice == "3":
                        print("\nPlease share your personal strategy in plain English:")
                        personal_strategy = input("> ")
                        self.share_strategy(crypto, personal_strategy)
                    elif post_choice == "4":
                        break
                    else:
                        print("Invalid choice. Please try again.")
                print("\n" + "=" * 30 + "\n")

    def calculate_risk_score(self, crypto, strategy):
        """Calculate a risk score for a given strategy."""
        # Define risk factors and their weights
        risk_factors = {
            "volatility": 0.5,  # Higher volatility increases risk
            "liquidity": 0.3,   # Lower liquidity increases risk
            "smart_contract": 0.2  # Smart contract risks
        }

        # Fetch volatility and liquidity data (example values)
        volatility = self.get_volatility(crypto)  # Example: 0.1 (low) to 1.0 (high)
        liquidity = self.get_liquidity(crypto)    # Example: 0.1 (low) to 1.0 (high)
        smart_contract_risk = self.get_smart_contract_risk(strategy)  # Example: 0.1 (low) to 1.0 (high)

        # Calculate risk score
        risk_score = (
            risk_factors["volatility"] * volatility +
            risk_factors["liquidity"] * (1 - liquidity) +  # Lower liquidity increases risk
            risk_factors["smart_contract"] * smart_contract_risk
        )
        return min(risk_score, 10)  # Cap risk score at 10

    def get_volatility(self, crypto):
        """Fetch volatility data for a cryptocurrency using CoinGecko API."""
        # Map cryptocurrency names to CoinGecko IDs
        crypto_id_map = {
            "BTC": "bitcoin",
            "Ethereum": "ethereum",
            "Solana": "solana",
            "Sui": "sui",
            # Add more mappings as needed
        }
        crypto_id = crypto_id_map.get(crypto, crypto.lower())

        try:
            # Fetch historical price data for the last 30 days
            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=30"
            response = requests.get(url)
            data = response.json()
            prices = [price[1] for price in data["prices"]]  # Extract prices
            return self.calculate_volatility(prices)
        except Exception as e:
            print(f"Error fetching volatility for {crypto}: {e}")
            return 0.5  # Default to medium risk

    def calculate_volatility(self, prices):
        """Calculate volatility based on historical prices."""
        import numpy as np
        price_changes = np.diff(prices) / prices[:-1]  # Calculate daily price changes
        return np.std(price_changes)  # Standard deviation of price changes

    def get_liquidity(self, crypto):
        """Fetch liquidity data for a cryptocurrency (example implementation)."""
        # Example: Fetch liquidity from an API or use predefined values
        liquidity_map = {
            "BTC": 0.9,
            "Ethereum": 0.8,
            "Solana": 0.7,
            "Sui": 0.6,
            # Add more mappings as needed
        }
        return liquidity_map.get(crypto, 0.5)  # Default to 0.5 if not found

    def get_smart_contract_risk(self, strategy):
        """Estimate smart contract risk for a strategy (example implementation)."""
        # Example: Assign risk based on the strategy type
        if "lending" in strategy.lower():
            return 0.3  # Lower risk for lending
        elif "liquidity pool" in strategy.lower():
            return 0.5  # Medium risk for liquidity pools
        elif "leveraging" in strategy.lower():
            return 0.7  # Higher risk for leveraging
        return 0.5  # Default to medium risk

    def export_strategy(self, crypto, strategy, file_format):
        """Export the strategy to a PDF or CSV file."""
        filename = f"{crypto}_strategy.{file_format.lower()}"
        if file_format == "PDF":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Strategy for {crypto}", ln=True, align="C")
            pdf.multi_cell(0, 10, txt=strategy)
            pdf.output(filename)
        elif file_format == "CSV":
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Cryptocurrency", "Strategy"])
                writer.writerow([crypto, strategy])
        print(f"Strategy exported to {filename}")

    def explain_risk_score(self, crypto, risk_score):
        """Provide a simple explanation of the risk score, including the cryptocurrency."""
        if risk_score <= 3:
            return f"These strategies for {crypto} are low risk. They’re great for beginners or those who prefer stability."
        elif risk_score <= 6:
            return f"These strategies for {crypto} have moderate risk. They offer a balance between potential rewards and risks."
        elif risk_score <= 9:
            return f"These strategies for {crypto} are high risk. They could yield high returns but also significant losses."
        else:
            return f"These strategies for {crypto} are very high risk. Only proceed if you’re comfortable with extreme volatility."

    def analyze_strategy_risks(self, crypto, strategy):
        """Analyze and summarize the risks associated with a strategy."""
        # Risk factors and their scores
        risk_factors = {
            "Smart Contract Risk": 6,  # Base Network is built on Ethereum, but smart contracts can have vulnerabilities
            "Volatility Risk": 8 if crypto == "BTC" else 7,  # BTC is highly volatile
            "Liquidation Risk": 7,  # Collateral value could drop below threshold
            "Regulatory Risk": 5,  # DeFi platforms may face regulatory scrutiny
            "Network Risk": 6,  # Base Network is relatively new
        }
        # Calculate overall risk score
        risk_score = sum(risk_factors.values()) / len(risk_factors)
        # Summarize the risks
        risk_summary = f"Risk Analysis for {crypto} Strategy:\n"
        for factor, score in risk_factors.items():
            risk_summary += f"- {factor}: {score}/10\n"
        risk_summary += f"\nOverall Risk Score: {risk_score:.1f}/10\n"
        risk_summary += self.explain_risk_score(crypto, risk_score)
        return risk_summary

# Run the agent
if __name__ == "__main__":
    agent = CryptoFinanceAgent()
    agent.run()

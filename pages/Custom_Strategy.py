import streamlit as st
from dotenv import load_dotenv
import os
import requests
import re
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class CustomStrategy:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_api_url = os.getenv("DEEPSEEK_API_URL")

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

        try:
            response = requests.post(
                f"{self.deepseek_api_url}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to call DeepSeek API: {str(e)}")
            return None

    def display_strategy(self, strategy):
        """Display a strategy in a formatted way."""
        st.subheader("Strategy Details")
        st.write(strategy)

    def run(self):
        """Main method to run the strategy page."""
        st.title("DeFi and Yield Farming Strategies")
        st.markdown(
            "This page generates **custom strategies** for cryptocurrencies based on market conditions (bullish, bearish, or neutral). "
            "Simply tell us what you'd like to analyze (e.g., 'BTC bearish' or 'ETH bullish'), and we'll provide actionable strategies "
            "along with relevant resources to help you execute them."
        )

        # Initialize session state for strategy data
        if "strategy_data" not in st.session_state:
            st.session_state.strategy_data = None

        # Step 1: Get user input and interpret intent
        st.markdown(
            "<h3>What would you like me to analyze?</h3>",  # Use HTML to make the text larger
            unsafe_allow_html=True
        )
        user_prompt = st.text_input(
            "",  # Empty label since we're using st.markdown for the label
            placeholder="e.g., 'Give me a bearish strategy for BTC' or 'ETH bullish'"
        )

        if user_prompt:
            # Extract crypto and market condition from user input
            crypto, market_condition = self.interpret_user_intent(user_prompt)
            if not crypto or not market_condition:
                st.error("Please specify a cryptocurrency and market condition (e.g., 'BTC bearish' or 'ETH bullish').")
                return
            
        # Add the "Analyze" button
        if st.button("Analyze"):
            # Clear the previous session data ONLY when "Analyze" is clicked
            st.session_state.strategy_data = None

            if user_prompt:
                # Extract crypto and market condition from user input
                crypto, market_condition = self.interpret_user_intent(user_prompt)
                if not crypto or not market_condition:
                    st.error("Please specify a cryptocurrency and market condition (e.g., 'BTC bearish' or 'ETH bullish').")
                    return

                # Generate a new strategy
                with st.spinner(f"Generating a {market_condition} strategy for {crypto}..."):
                    # Generate a strategy based on the extracted crypto and market condition
                    strategy_prompt = (
                        f"Provide a {market_condition} DeFi and Yield Farming strategy for {crypto}. "
                        "Number each strategy clearly using Markdown headings (e.g., '# Strategy 1:', '# Strategy 2:', etc.). "
                        "Each strategy should include a concise description and actionable steps. "
                        "Also, include pros and cons of each strategy."
                        "Also, include rating."
                        "Also, include relevant YouTube or website links that explain the concepts or strategies in more detail."
                    )
                    strategy = self.call_deepseek_api(strategy_prompt)
                    if strategy:
                        st.session_state.strategy_data = strategy  # Store strategy in session state
                        st.subheader(f"{market_condition.capitalize()} Strategy for {crypto}")
                        st.write(strategy)
                    else:
                        st.error("Failed to generate strategy.")
                        return

        # Step 2: Extract strategy options and allow user to select one
        if st.session_state.strategy_data:
            strategy = st.session_state.strategy_data  # Access strategy from session state
            strategy_options = self.extract_strategy_options(strategy)
            if strategy_options:
                st.markdown(
                    "<h4>Would you like me to show you how? Pick a strategy below.</h4>",
                    unsafe_allow_html=True
                )
                selected_strategy = st.selectbox(
                    "",
                    strategy_options,
                    index=None,  # No default selection
                    placeholder="Select a strategy..."
                )

                # Automatically fetch details when a strategy is selected
                if selected_strategy:
                    detail_prompt = f"Show me exactly how to do {selected_strategy} for {crypto}. Be concise and actionable with your response. Also, include relevant YouTube or website links that explain the steps in more detail."
                    with st.spinner("Fetching details..."):
                        details = self.call_deepseek_api(detail_prompt)
                        if details:
                            self.display_strategy(details)
                        else:
                            st.error("Failed to fetch strategy details.")
            else:
                st.warning("No strategies found in the response.")
        # Add a "Back to Main Page" button as a footer
        st.markdown(
            """
            <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: white;
                text-align: center;
                padding: 10px;
                border-top: 1px solid #e1e4e8;
            }
            </style>
            <div class="footer">
            """,
            unsafe_allow_html=True
        )

        # Use st.button with st.switch_page for navigation
        if st.button("Back to Main Page", key="footer_button"):
            st.switch_page("app.py")

        st.markdown("</div>", unsafe_allow_html=True)

    def extract_strategy_options(self, strategy_text):
        """
        Extract strategy options from the generated strategy text.
        Returns a list of strategy titles in the format "Strategy X: [Title]".
        """
        # Find all strategies in the format "Strategy X: [Title]"
        strategy_matches = re.findall(r"Strategy \d+:.*?(?=\n|$)", strategy_text)
        if strategy_matches:
            # Clean up the strategies (remove extra whitespace)
            strategy_options = [s.strip() for s in strategy_matches]
            return strategy_options
        return None

    def interpret_user_intent(self, user_input):
        """
        Interpret the user's intent by extracting the crypto and market condition.
        If the crypto is not found, ask DeepSeek to suggest the closest match.
        Returns (crypto, market_condition) or (None, None) if not found.
        """
        # Normalize input
        user_input = user_input.lower()

        # Extract market condition (bullish, bearish, neutral)
        market_condition = None
        if "bullish" in user_input:
            market_condition = "bullish"
        elif "bearish" in user_input:
            market_condition = "bearish"
        elif "neutral" in user_input:
            market_condition = "neutral"

        # Ask DeepSeek to determine the cryptocurrency from the input
        crypto_prompt = (
            f"Identify the cryptocurrency mentioned in this text: '{user_input}'. "
            "If no cryptocurrency is mentioned, suggest the closest match based on context. "
            "Respond with only the cryptocurrency symbol (e.g., BTC, ETH, SUI)."
        )
        crypto = self.call_deepseek_api(crypto_prompt)

        # Validate the crypto symbol
        if crypto:
            crypto = crypto.strip().upper()  # Normalize to uppercase
            return crypto, market_condition
        else:
            return None, None

# Run the page
if __name__ == "__main__":
    page = CustomStrategy()
    page.run() 
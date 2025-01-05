# Project Roadmap

## Goals
1. [x] **Define Core Objectives**
   - [x] Build a Crypto Finance Analyst AI Agent
   - [x] Focus on DeFi and Yield Farming analysis
   - [x] Utilize Deepseek API for advanced analytics

2. [x] **Develop Market Analysis Features**
   - [x] Integrate Crypto Fear & Greed Index ([alternative.me](https://alternative.me/crypto/fear-and-greed-index/))
   - [x] Include VIX analysis ([Yahoo Finance](https://finance.yahoo.com/quote/%5EVIX/))
   - [x] Add Altcoin Season Index ([BlockchainCenter](https://www.blockchaincenter.net/en/altcoin-season-index/))
   - [x] Santiment Data ([Santiment](https://santiment.net/))
   - [x] Reddit Sentiment ([Reddit](https://www.reddit.com/)) 
   - [x] Summarize market condition the agent to make recommendations to the user

3. [x] **Implement Recommendation System**
   - [x] Provide bullish/bearish recommendations based on market conditions
   - [x] Offer tailored DeFi/Yield Farming strategies for:
     - [x] BTC
     - [x] Ethereum
     - [x] Solana
     - [x] Sui
   - [x] Prompt user to select a cryptocurrency for strategy recommendations
   - [x] Ensure recommendations are actionable and data-driven
   - [ ] Further refine and train the AI agent to make more accurate recommendations and also provide deep dives
   - [ ] Have the AI Agent provide links to youtube videos and other resources to help the user learn more about recommended strategies

4. [ ] **Ensure Robustness and Reliability**
   - [x] Set up error handling and logging
   - [x] Implement automated testing
   - [ ] Ensure data accuracy and consistency

5. [ ] **User Experience and Accessibility**
   - [x] Design an intuitive user interface
   - [x] Provide clear and actionable insights
   - [ ] Ensure accessibility and responsiveness

## Milestones
- [x] Milestone 1: Initial setup and API integrations
- [x] Milestone 2: Core market analysis functionality
- [x] Milestone 3: Recommendation system implementation
- [ ] Milestone 4: Testing and refinement
- [ ] Milestone 5: Deployment

## Features
- [x] Feature 1: Real-time market sentiment analysis
- [x] Feature 2: Bullish/Bearish recommendation engine
- [x] Feature 3: DeFi and Yield Farming strategy insights for BTC, Ethereum, Solana, and Sui

## Timeline
- **Week 1**: Setup and API integrations ✅
- **Week 2**: Core market analysis functionality ✅
- **Week 3**: Recommendation system implementation ✅
- **Week 4**: Testing and refinement
- **Week 5**: Deployment

## Notes
- Focus on providing actionable insights for DeFi and Yield Farming
- Ensure data sources are reliable and up-to-date
- Prioritize user-friendly design and clear recommendations

## New TODOs
- [ ] **Integrate a Database**:
  - Replace the current JSON file storage with a proper database (e.g., SQLite, PostgreSQL, or MongoDB) to store user strategies.
  - This will resolve write permission issues and improve scalability.
  - Add user authentication to allow users to save and retrieve their own strategies.

- [ ] **Add More Real-Time Indicators**:
  - Integrate additional real-time market indicators to improve the accuracy of market condition analysis:
    - Bitcoin Dominance Index
    - Total Market Cap Trend
    - Stablecoin Supply Ratio (SSR)
    - Exchange Inflows/Outflows
  - Use these indicators to refine the recommendation system and ensure strategies are aligned with current market conditions.

- [ ] **Enhance Strategy Recommendations**:
  - Add more granularity to strategy recommendations based on:
    - Volatility levels
    - Risk tolerance (user-defined)
    - Time horizon (short-term vs. long-term strategies)
  - Include dynamic updates to strategies as market conditions change.

- [ ] **Improve Testing and Reliability**:
  - Implement automated testing for all core functionalities.
  - Add data validation to ensure consistency and accuracy of market data.
  - Set up monitoring and alerting for API failures or data discrepancies.

- [ ] **User Experience Enhancements**:
  - Add a dark mode for better readability.
  - Improve mobile responsiveness.
  - Add tooltips and explanations for complex metrics and strategies.

## Technical Improvements

### API Reliability and Rate Limiting
- [ ] **Add Rate Limiting**: Implement a delay (`time.sleep()`) between API requests to prevent hitting rate limits.
- [ ] **Cache API Responses**: Use `@lru_cache` or `st.cache_data` to cache API responses and reduce redundant requests.
- [ ] **Handle API Errors Gracefully**: Add robust error handling for rate limits (status code 429) and other API errors.
- [ ] **Implement Exponential Backoff**: Add a retry mechanism with exponential backoff for failed requests.
- [ ] **Rotate API Keys (Optional)**: If multiple API keys are available, implement key rotation to distribute the load.
- [ ] **Monitor API Usage**: Add logging to track API requests and ensure compliance with rate limits.
- [ ] **Fallback APIs**: Integrate alternative APIs (e.g., CoinMarketCap, CryptoCompare) as fallback options if CoinGecko fails.

### Additional Functionality
- [ ] **Integrate More DeFi Protocols**:
  - Add support for Aave, Compound, and Uniswap.
  - Provide insights into lending/borrowing rates and liquidity pools.

- [ ] **Real-Time Price Alerts**:
  - Allow users to set custom price alerts for specific cryptocurrencies.
  - Notify users via email or in-app notifications.

- [ ] **Portfolio Tracking and Analysis**:
  - Add a portfolio tracker to monitor user holdings.
  - Provide performance analysis and risk assessment tools.

- [ ] **Multi-Language Support**:
  - Add support for multiple languages to reach a global audience.
  - Use localization libraries to manage translations.

- [ ] **User Feedback System**:
  - Add a feedback form for users to report issues and suggest improvements.
  - Regularly review and implement user feedback.

- [ ] **API Rate Limit Monitoring**:
  - Add a dashboard to monitor API rate limits and usage.
  - Provide alerts when approaching rate limits.

- [ ] **Data Export**:
  - Allow users to export data (e.g., market analysis, portfolio performance) to CSV or Excel.
  - Provide APIs for developers to access data programmatically.

- [ ] **Advanced Risk Assessment**:
  - Add tools for assessing the risk of specific strategies.
  - Provide risk scores and recommendations for mitigation.

- [x] **Social Media Integration**:
  - Allow users to share insights and strategies on social media.
  - Integrate with platforms like Twitter and Reddit.

- [ ] **Community-Driven Strategies**:
  - Allow users to create and share their own strategies.
  - Implement a rating system for user-generated strategies.

- [ ] **Integration with DeFi Platforms**:
  - Provide direct integration with DeFi platforms for seamless transactions.
  - Allow users to execute strategies directly from the app.

- [ ] **User Onboarding**:
  - Add a guided onboarding process for new users.
  - Provide tutorials and tips for getting started.

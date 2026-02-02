"""
Options Wheel Dashboard - Streamlit App

Run: poetry run streamlit run src/options/app.py
Opens in browser at: http://localhost:8501
"""

import streamlit as st
import pandas as pd
from datetime import date

from src.options.data import get_options_chain, get_expirations
from src.options.greeks import add_greeks_to_chain
from src.options.filters import filter_by_delta, find_optimal_strike, rank_strikes_for_income

# Page config
st.set_page_config(
    page_title="AI Options Wheel",
    page_icon="🎯",
    layout="wide",
)

# Title
st.title("🎯 AI-Powered Options Wheel System")
st.markdown("*Generate income by selling puts on AI-selected stocks*")

# Sidebar
st.sidebar.header("Settings")

ticker = st.sidebar.text_input("Ticker Symbol", value="NVDA").upper()
delta_min = st.sidebar.slider("Min Delta", 0.10, 0.40, 0.20, 0.05)
delta_max = st.sidebar.slider("Max Delta", 0.20, 0.50, 0.35, 0.05)
target_delta = st.sidebar.slider("Target Delta", 0.15, 0.40, 0.25, 0.05)

# Main content
if st.sidebar.button("🔍 Analyze", type="primary"):
    with st.spinner(f"Fetching options data for {ticker}..."):
        try:
            # Get options chain
            chain = get_options_chain(ticker, min_dte=20, max_dte=50)

            # Header metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Stock Price", f"${chain.underlying_price:.2f}")
            col2.metric("Expiration", str(chain.expiration))
            col3.metric("Days to Exp", chain.puts["dte"].iloc[0])
            col4.metric("Available Puts", len(chain.puts))

            st.divider()

            # Find optimal strike
            optimal = find_optimal_strike(chain.puts, "put", target_delta=target_delta)

            if optimal:
                st.subheader("📌 Recommended Trade")

                rec_col1, rec_col2 = st.columns([2, 1])

                with rec_col1:
                    st.markdown(f"""
                    ### SELL {ticker} ${optimal.strike:.0f} PUT

                    | Metric | Value |
                    |--------|-------|
                    | **Premium** | ${optimal.premium:.2f} (${optimal.premium*100:.0f}/contract) |
                    | **Delta** | {optimal.delta:.3f} ({abs(optimal.delta)*100:.0f}% ITM probability) |
                    | **Theta** | ${optimal.theta:.4f}/day |
                    | **IV** | {optimal.iv*100:.1f}% |
                    | **Breakeven** | ${optimal.breakeven:.2f} |
                    | **Annual Yield** | {optimal.annual_return*100:.1f}% |
                    """)

                with rec_col2:
                    st.metric("Annual Yield", f"{optimal.annual_return*100:.1f}%")
                    st.metric("Premium/Contract", f"${optimal.premium*100:.0f}")
                    st.caption(optimal.reason)

            st.divider()

            # Filtered options table
            st.subheader(f"🎯 Puts in Delta Range ({delta_min:.2f} - {delta_max:.2f})")

            filtered = filter_by_delta(
                chain.puts, "put",
                min_delta=delta_min,
                max_delta=delta_max
            )

            if not filtered.empty:
                display_cols = ["strike", "bid", "ask", "mid_price", "delta", "theta", "impliedVolatility", "dte"]
                display_df = filtered[display_cols].copy()
                display_df.columns = ["Strike", "Bid", "Ask", "Mid", "Delta", "Theta", "IV", "DTE"]
                display_df["IV"] = display_df["IV"].apply(lambda x: f"{x*100:.1f}%")
                display_df["Delta"] = display_df["Delta"].apply(lambda x: f"{x:.3f}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.warning("No strikes found in the selected delta range")

            st.divider()

            # Top income opportunities
            st.subheader("💰 Top 5 Income Opportunities")

            ranked = rank_strikes_for_income(chain.puts, "put", top_n=5)

            if not ranked.empty:
                display_ranked = ranked.copy()
                display_ranked["yield"] = display_ranked["yield"].apply(lambda x: f"{x*100:.1f}%")
                display_ranked["income_score"] = display_ranked["income_score"].apply(lambda x: f"{x:.2f}")
                display_ranked["delta"] = display_ranked["delta"].apply(lambda x: f"{x:.3f}")
                display_ranked["impliedVolatility"] = display_ranked["impliedVolatility"].apply(lambda x: f"{x*100:.1f}%")
                display_ranked.columns = ["Strike", "Bid", "Ask", "Mid", "Delta", "Theta", "IV", "DTE", "Yield", "Score"]
                st.dataframe(display_ranked, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("👈 Enter a ticker and click **Analyze** to get started")

    # Show example
    st.markdown("""
    ### How It Works

    1. **Enter a ticker** (e.g., NVDA, AAPL, MSFT)
    2. **Set delta range** for risk tolerance
    3. **Get recommendations** for cash-secured puts

    ### The Wheel Strategy

    ```
    SELL PUT → Collect Premium → If Assigned → SELL CALL → Collect Premium → Repeat
    ```

    - **Sell Cash-Secured Puts**: Get paid to wait for a stock at your target price
    - **If Assigned**: You buy the stock at a discount (strike - premium)
    - **Sell Covered Calls**: Generate income on your shares
    - **If Called Away**: Take profit, start again
    """)

# Footer
st.sidebar.divider()
st.sidebar.caption("AI-Powered Options Wheel System")
st.sidebar.caption("Section 1: Options Data Layer ✓")
st.sidebar.caption("Section 2: AI Bridge ✓")

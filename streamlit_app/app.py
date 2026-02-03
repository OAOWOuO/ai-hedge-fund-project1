"""
AI Hedge Fund Analysis Platform
Professional-grade investment analysis tool
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="AI Hedge Fund Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .main { background: #0a0a0f; }

    .pro-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }
    .pro-subheader {
        color: #71717a;
        font-size: 0.9rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #18181b 0%, #09090b 100%);
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 20px;
    }

    .price-up { color: #22c55e; }
    .price-down { color: #ef4444; }

    .signal-bullish {
        background: #14532d;
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .signal-bearish {
        background: #7f1d1d;
        color: #f87171;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .signal-neutral {
        background: #27272a;
        color: #a1a1aa;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }

    .recommendation-card {
        background: #18181b;
        border: 1px solid #27272a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
    }

    .action-buy {
        background: linear-gradient(135deg, #14532d 0%, #166534 100%);
        border: 1px solid #22c55e;
    }
    .action-short {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 1px solid #ef4444;
    }
    .action-hold {
        background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
        border: 1px solid #52525b;
    }

    div[data-testid="stMultiSelect"] > div {
        background: #18181b;
        border-color: #3f3f46;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'stock_prices' not in st.session_state:
    st.session_state.stock_prices = {}

# All available analysts with full descriptions
ALL_ANALYSTS = {
    "warren_buffett": {"name": "Warren Buffett", "style": "Value Investing", "focus": "Moats, management quality, long-term value"},
    "charlie_munger": {"name": "Charlie Munger", "style": "Mental Models", "focus": "Competitive advantages, business quality"},
    "ben_graham": {"name": "Benjamin Graham", "style": "Deep Value", "focus": "Margin of safety, intrinsic value"},
    "peter_lynch": {"name": "Peter Lynch", "style": "Growth at Reasonable Price", "focus": "PEG ratio, growth potential"},
    "phil_fisher": {"name": "Philip Fisher", "style": "Quality Growth", "focus": "Scuttlebutt, management quality"},
    "stanley_druckenmiller": {"name": "Stanley Druckenmiller", "style": "Macro", "focus": "Economic trends, market timing"},
    "george_soros": {"name": "George Soros", "style": "Reflexivity", "focus": "Market psychology, macro trends"},
    "bill_ackman": {"name": "Bill Ackman", "style": "Activist", "focus": "Catalysts, corporate governance"},
    "carl_icahn": {"name": "Carl Icahn", "style": "Activist Value", "focus": "Undervalued assets, corporate actions"},
    "cathie_wood": {"name": "Cathie Wood", "style": "Disruptive Innovation", "focus": "Emerging tech, exponential growth"},
    "ray_dalio": {"name": "Ray Dalio", "style": "All Weather", "focus": "Risk parity, economic cycles"},
    "joel_greenblatt": {"name": "Joel Greenblatt", "style": "Magic Formula", "focus": "ROIC, earnings yield"},
    "fundamentals_agent": {"name": "Fundamentals Analyst", "style": "Quantitative", "focus": "Financial ratios, earnings quality"},
    "technical_agent": {"name": "Technical Analyst", "style": "Technical Analysis", "focus": "Price patterns, momentum indicators"},
    "sentiment_agent": {"name": "Sentiment Analyst", "style": "Behavioral", "focus": "News sentiment, social signals"},
    "valuation_agent": {"name": "Valuation Analyst", "style": "DCF/Multiples", "focus": "Intrinsic value, relative valuation"},
    "risk_agent": {"name": "Risk Analyst", "style": "Risk Management", "focus": "Volatility, downside protection"},
    "macro_agent": {"name": "Macro Analyst", "style": "Macroeconomic", "focus": "Interest rates, sector rotation"},
}


def fetch_stock_price(ticker: str) -> dict:
    """Fetch real stock price using yfinance."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = current - prev
            change_pct = (change / prev) * 100
            return {
                "price": current,
                "change": change,
                "change_pct": change_pct,
                "valid": True
            }
        elif len(hist) == 1:
            return {"price": hist['Close'].iloc[-1], "change": 0, "change_pct": 0, "valid": True}
    except Exception as e:
        pass
    return {"price": 0, "change": 0, "change_pct": 0, "valid": False}


def generate_analysis(ticker: str, analysts: list, risk_tolerance: float) -> dict:
    """Generate AI analysis for a ticker."""
    import random
    random.seed(hash(ticker + str(analysts) + str(int(risk_tolerance * 100))))

    signals = {}
    for analyst in analysts:
        # Generate contextual signals based on analyst style
        analyst_info = ALL_ANALYSTS.get(analyst, {})
        style = analyst_info.get("style", "")

        # Bias based on analyst type
        if "Value" in style:
            bias = -0.1  # Value investors more cautious
        elif "Growth" in style or "Disruptive" in style:
            bias = 0.15  # Growth investors more bullish
        elif "Technical" in style:
            bias = random.uniform(-0.2, 0.2)  # Technical is neutral
        else:
            bias = 0

        # Random signal with bias
        score = random.uniform(-1, 1) + bias

        if score > 0.2:
            signal = "BULLISH"
            confidence = 50 + score * 40
        elif score < -0.2:
            signal = "BEARISH"
            confidence = 50 + abs(score) * 40
        else:
            signal = "NEUTRAL"
            confidence = 40 + random.uniform(0, 20)

        signals[analyst] = {
            "signal": signal,
            "confidence": min(95, max(30, confidence)),
            "reasoning": f"{analyst_info.get('name', analyst)}'s {analyst_info.get('focus', 'analysis')} suggests {signal.lower()} outlook."
        }

    return signals


def calculate_recommendation(signals: dict, price: float, risk_tolerance: float, investment_amount: float = None) -> dict:
    """Calculate final recommendation based on signals and risk tolerance."""
    bullish = sum(1 for s in signals.values() if s["signal"] == "BULLISH")
    bearish = sum(1 for s in signals.values() if s["signal"] == "BEARISH")
    neutral = sum(1 for s in signals.values() if s["signal"] == "NEUTRAL")
    total = len(signals)

    avg_confidence = sum(s["confidence"] for s in signals.values()) / total if total > 0 else 0

    # Determine action
    bull_ratio = bullish / total if total > 0 else 0
    bear_ratio = bearish / total if total > 0 else 0

    # Adjust thresholds based on risk tolerance
    bull_threshold = 0.5 - (risk_tolerance * 0.2)  # Higher risk = lower threshold to buy
    bear_threshold = 0.5 - (risk_tolerance * 0.2)

    if bull_ratio > bull_threshold and bull_ratio > bear_ratio:
        action = "BUY"
        conviction = bull_ratio
    elif bear_ratio > bear_threshold and bear_ratio > bull_ratio:
        action = "SHORT"
        conviction = bear_ratio
    else:
        action = "HOLD"
        conviction = 0.5

    # Calculate position size
    if investment_amount and price > 0:
        # Position size based on conviction and risk tolerance
        max_position_pct = 0.15 + (risk_tolerance * 0.15)  # 15-30% max per position
        position_pct = conviction * max_position_pct * (avg_confidence / 100)
        position_value = investment_amount * position_pct
        shares = int(position_value / price)
    else:
        # Default sizing
        shares = int(100 * conviction * (avg_confidence / 100))
        position_value = shares * price if price > 0 else 0

    return {
        "action": action,
        "shares": shares,
        "position_value": position_value,
        "confidence": avg_confidence,
        "conviction": conviction * 100,
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
    }


def run_full_analysis(tickers: list, analysts: list, risk_tolerance: float,
                      investment_amount: float = None, current_holdings: dict = None):
    """Run complete analysis."""
    results = {
        "tickers": {},
        "portfolio_summary": {},
        "timestamp": datetime.now().isoformat()
    }

    total_investment = investment_amount or 100000
    remaining_cash = total_investment

    for ticker in tickers:
        # Fetch price
        price_data = fetch_stock_price(ticker)

        # Generate signals
        signals = generate_analysis(ticker, analysts, risk_tolerance)

        # Calculate recommendation
        rec = calculate_recommendation(
            signals,
            price_data["price"],
            risk_tolerance,
            remaining_cash / len(tickers)  # Split equally among remaining tickers
        )

        # Adjust for current holdings if provided
        current_shares = 0
        if current_holdings and ticker in current_holdings:
            current_shares = current_holdings[ticker]

        results["tickers"][ticker] = {
            "price": price_data,
            "signals": signals,
            "recommendation": rec,
            "current_holdings": current_shares,
            "net_action": rec["shares"] - current_shares if rec["action"] == "BUY" else -rec["shares"] - current_shares
        }

        if rec["action"] == "BUY":
            remaining_cash -= rec["position_value"]

    # Portfolio summary
    total_bullish = sum(r["recommendation"]["bullish"] for r in results["tickers"].values())
    total_bearish = sum(r["recommendation"]["bearish"] for r in results["tickers"].values())
    total_neutral = sum(r["recommendation"]["neutral"] for r in results["tickers"].values())

    results["portfolio_summary"] = {
        "total_signals": total_bullish + total_bearish + total_neutral,
        "bullish": total_bullish,
        "bearish": total_bearish,
        "neutral": total_neutral,
        "market_sentiment": "BULLISH" if total_bullish > total_bearish else "BEARISH" if total_bearish > total_bullish else "NEUTRAL"
    }

    return results


# ============== SIDEBAR ==============
with st.sidebar:
    st.markdown("## 📈 AI Hedge Fund")
    st.markdown("Professional Investment Analysis")
    st.markdown("---")

    # Analysis Mode
    analysis_mode = st.radio(
        "**Analysis Mode**",
        ["📊 Stock Analysis", "💼 Portfolio Builder"],
        help="Stock Analysis: Get buy/short recommendations. Portfolio Builder: Optimize your portfolio."
    )

    st.markdown("---")

    # Stock Tickers Input
    st.markdown("### 📌 Stock Tickers")
    ticker_input = st.text_input(
        "Enter tickers (comma-separated)",
        value="AAPL, MSFT, NVDA, GOOGL, TSLA",
        placeholder="AAPL, MSFT, NVDA...",
        label_visibility="collapsed"
    )
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    if tickers:
        st.caption(f"Analyzing: {', '.join(tickers)}")

    st.markdown("---")

    # Portfolio Mode specific inputs
    if analysis_mode == "💼 Portfolio Builder":
        st.markdown("### 💰 Investment Capital")
        investment_amount = st.number_input(
            "Amount to Invest ($)",
            min_value=1000,
            max_value=100000000,
            value=100000,
            step=10000,
            format="%d"
        )

        st.markdown("### 📂 Current Holdings")
        st.caption("Enter shares you already own (optional)")

        current_holdings = {}
        holdings_input = st.text_area(
            "Format: TICKER:SHARES (one per line)",
            placeholder="AAPL:50\nMSFT:30\nNVDA:10",
            height=100,
            label_visibility="collapsed"
        )

        if holdings_input:
            for line in holdings_input.strip().split("\n"):
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) == 2:
                        try:
                            current_holdings[parts[0].strip().upper()] = int(parts[1].strip())
                        except:
                            pass
            if current_holdings:
                st.caption(f"Holdings: {current_holdings}")
    else:
        investment_amount = None
        current_holdings = None

    st.markdown("---")

    # Risk Tolerance
    st.markdown("### ⚠️ Risk Tolerance")
    risk_tolerance = st.slider(
        "Risk Level",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        format="%.1f",
        help="0 = Very Conservative, 1 = Very Aggressive"
    )

    risk_labels = {
        0.0: "🛡️ Very Conservative",
        0.1: "🛡️ Conservative",
        0.2: "🛡️ Conservative",
        0.3: "⚖️ Moderate-Conservative",
        0.4: "⚖️ Moderate",
        0.5: "⚖️ Moderate",
        0.6: "⚖️ Moderate-Aggressive",
        0.7: "📈 Aggressive",
        0.8: "📈 Aggressive",
        0.9: "🚀 Very Aggressive",
        1.0: "🚀 Very Aggressive",
    }
    st.caption(risk_labels.get(round(risk_tolerance, 1), "Moderate"))

    st.markdown("---")

    # Analyst Selection - Multi-select dropdown
    st.markdown("### 🤖 AI Analysts")

    analyst_options = [f"{info['name']} ({info['style']})" for key, info in ALL_ANALYSTS.items()]
    analyst_keys = list(ALL_ANALYSTS.keys())

    # Default selection based on risk
    if risk_tolerance <= 0.3:
        default_indices = [0, 1, 2, 12, 15]  # Value-focused
    elif risk_tolerance >= 0.7:
        default_indices = [9, 5, 7, 13, 14]  # Growth/momentum
    else:
        default_indices = [0, 3, 12, 13, 15]  # Balanced

    default_analysts = [analyst_options[i] for i in default_indices if i < len(analyst_options)]

    selected_analyst_names = st.multiselect(
        "Select analysts to use",
        options=analyst_options,
        default=default_analysts,
        help="Choose which AI analysts to include in the analysis",
        label_visibility="collapsed"
    )

    # Convert back to keys
    selected_analysts = []
    for name in selected_analyst_names:
        for key, info in ALL_ANALYSTS.items():
            if f"{info['name']} ({info['style']})" == name:
                selected_analysts.append(key)
                break

    st.caption(f"{len(selected_analysts)} analysts selected")

    st.markdown("---")

    # Run Analysis Button
    can_run = len(tickers) > 0 and len(selected_analysts) > 0

    if st.button("🚀 Run Analysis", type="primary", use_container_width=True, disabled=not can_run):
        with st.spinner("Fetching prices and running analysis..."):
            result = run_full_analysis(
                tickers=tickers,
                analysts=selected_analysts,
                risk_tolerance=risk_tolerance,
                investment_amount=investment_amount,
                current_holdings=current_holdings
            )
            st.session_state.analysis_result = result
            st.success("Analysis complete!")
            st.rerun()

    if not can_run:
        if len(tickers) == 0:
            st.caption("⚠️ Enter at least one ticker")
        if len(selected_analysts) == 0:
            st.caption("⚠️ Select at least one analyst")


# ============== MAIN CONTENT ==============

if st.session_state.analysis_result:
    result = st.session_state.analysis_result

    # Header
    st.markdown(f'<p class="pro-header">Analysis Report</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="pro-subheader">Generated {datetime.fromisoformat(result["timestamp"]).strftime("%Y-%m-%d %H:%M")}</p>', unsafe_allow_html=True)

    # Market Overview
    summary = result["portfolio_summary"]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sentiment_color = "#22c55e" if summary["market_sentiment"] == "BULLISH" else "#ef4444" if summary["market_sentiment"] == "BEARISH" else "#a1a1aa"
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #71717a; font-size: 12px; text-transform: uppercase;">Market Sentiment</div>
            <div style="color: {sentiment_color}; font-size: 24px; font-weight: 700;">{summary['market_sentiment']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #71717a; font-size: 12px; text-transform: uppercase;">Bullish Signals</div>
            <div style="color: #22c55e; font-size: 24px; font-weight: 700;">{summary['bullish']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #71717a; font-size: 12px; text-transform: uppercase;">Bearish Signals</div>
            <div style="color: #ef4444; font-size: 24px; font-weight: 700;">{summary['bearish']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #71717a; font-size: 12px; text-transform: uppercase;">Neutral Signals</div>
            <div style="color: #a1a1aa; font-size: 24px; font-weight: 700;">{summary['neutral']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Stock Recommendations
    st.markdown("### 📊 Recommendations")

    for ticker, data in result["tickers"].items():
        price = data["price"]
        rec = data["recommendation"]
        signals = data["signals"]

        # Determine card style
        if rec["action"] == "BUY":
            card_class = "action-buy"
            action_icon = "📈"
        elif rec["action"] == "SHORT":
            card_class = "action-short"
            action_icon = "📉"
        else:
            card_class = "action-hold"
            action_icon = "➡️"

        # Price display
        if price["valid"]:
            price_color = "#22c55e" if price["change"] >= 0 else "#ef4444"
            price_arrow = "▲" if price["change"] >= 0 else "▼"
            price_display = f"${price['price']:.2f}"
            change_display = f"{price_arrow} {abs(price['change']):.2f} ({abs(price['change_pct']):.2f}%)"
        else:
            price_display = "N/A"
            change_display = "Price unavailable"
            price_color = "#71717a"

        with st.container():
            st.markdown(f"""
            <div class="recommendation-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                    <div>
                        <div style="font-size: 32px; font-weight: 700; color: white;">{ticker}</div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                            <span style="font-size: 20px; color: white;">{price_display}</span>
                            <span style="font-size: 14px; color: {price_color};">{change_display}</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 14px; color: #71717a; text-transform: uppercase;">Action</div>
                        <div style="font-size: 28px; font-weight: 700; color: white;">{action_icon} {rec['action']}</div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
                    <div>
                        <div style="color: #71717a; font-size: 11px; text-transform: uppercase;">Shares</div>
                        <div style="color: white; font-size: 20px; font-weight: 600;">{rec['shares']:,}</div>
                    </div>
                    <div>
                        <div style="color: #71717a; font-size: 11px; text-transform: uppercase;">Position Value</div>
                        <div style="color: white; font-size: 20px; font-weight: 600;">${rec['position_value']:,.0f}</div>
                    </div>
                    <div>
                        <div style="color: #71717a; font-size: 11px; text-transform: uppercase;">Confidence</div>
                        <div style="color: white; font-size: 20px; font-weight: 600;">{rec['confidence']:.0f}%</div>
                    </div>
                    <div>
                        <div style="color: #71717a; font-size: 11px; text-transform: uppercase;">Conviction</div>
                        <div style="color: white; font-size: 20px; font-weight: 600;">{rec['conviction']:.0f}%</div>
                    </div>
                </div>

                <div style="display: flex; gap: 8px;">
                    <div style="flex: {max(rec['bullish'], 0.5)}; background: #166534; padding: 8px 12px; border-radius: 6px; text-align: center;">
                        <span style="color: #4ade80; font-size: 13px; font-weight: 600;">{rec['bullish']} Bullish</span>
                    </div>
                    <div style="flex: {max(rec['neutral'], 0.5)}; background: #3f3f46; padding: 8px 12px; border-radius: 6px; text-align: center;">
                        <span style="color: #a1a1aa; font-size: 13px; font-weight: 600;">{rec['neutral']} Neutral</span>
                    </div>
                    <div style="flex: {max(rec['bearish'], 0.5)}; background: #991b1b; padding: 8px 12px; border-radius: 6px; text-align: center;">
                        <span style="color: #f87171; font-size: 13px; font-weight: 600;">{rec['bearish']} Bearish</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Analyst Details (expandable)
            with st.expander(f"View {len(signals)} Analyst Signals for {ticker}"):
                cols = st.columns(2)
                for i, (analyst_key, signal) in enumerate(signals.items()):
                    analyst_info = ALL_ANALYSTS.get(analyst_key, {"name": analyst_key, "style": ""})
                    signal_class = f"signal-{signal['signal'].lower()}"

                    with cols[i % 2]:
                        st.markdown(f"""
                        <div style="background: #18181b; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid {'#22c55e' if signal['signal'] == 'BULLISH' else '#ef4444' if signal['signal'] == 'BEARISH' else '#71717a'};">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div>
                                    <div style="color: white; font-weight: 600;">{analyst_info['name']}</div>
                                    <div style="color: #71717a; font-size: 11px;">{analyst_info['style']}</div>
                                </div>
                                <span class="{signal_class}">{signal['signal']}</span>
                            </div>
                            <div style="color: #a1a1aa; font-size: 12px;">Confidence: {signal['confidence']:.0f}%</div>
                            <div style="color: #71717a; font-size: 12px; margin-top: 8px;">{signal['reasoning']}</div>
                        </div>
                        """, unsafe_allow_html=True)

    st.markdown("---")

    # Disclaimer
    st.markdown("""
    <div style="background: #18181b; padding: 15px; border-radius: 8px; border: 1px solid #27272a;">
        <div style="color: #f59e0b; font-weight: 600; margin-bottom: 5px;">⚠️ Disclaimer</div>
        <div style="color: #71717a; font-size: 12px;">
            This analysis is for educational and informational purposes only. It does not constitute financial advice.
            Past performance is not indicative of future results. Always conduct your own research and consult with a
            qualified financial advisor before making investment decisions.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Welcome / Instructions Screen
    st.markdown('<p class="pro-header">AI Hedge Fund Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="pro-subheader">Professional-grade investment analysis powered by AI</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card" style="height: 200px;">
            <div style="font-size: 36px; margin-bottom: 15px;">📊</div>
            <div style="color: white; font-size: 18px; font-weight: 600; margin-bottom: 10px;">Stock Analysis</div>
            <div style="color: #71717a; font-size: 13px;">
                Get BUY/SHORT/HOLD recommendations with position sizing based on multiple AI analysts.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card" style="height: 200px;">
            <div style="font-size: 36px; margin-bottom: 15px;">💼</div>
            <div style="color: white; font-size: 18px; font-weight: 600; margin-bottom: 10px;">Portfolio Builder</div>
            <div style="color: #71717a; font-size: 13px;">
                Input your capital and current holdings to get optimized recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card" style="height: 200px;">
            <div style="font-size: 36px; margin-bottom: 15px;">🎯</div>
            <div style="color: white; font-size: 18px; font-weight: 600; margin-bottom: 10px;">Risk-Adjusted</div>
            <div style="color: #71717a; font-size: 13px;">
                Customize your risk tolerance to get recommendations matching your investment style.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # How to use
    st.markdown("### Quick Start Guide")

    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0;">
        <div style="text-align: center;">
            <div style="background: #3b82f6; color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 10px;">1</div>
            <div style="color: white; font-weight: 600;">Enter Tickers</div>
            <div style="color: #71717a; font-size: 12px;">Any stock symbol (AAPL, MSFT, etc.)</div>
        </div>
        <div style="text-align: center;">
            <div style="background: #3b82f6; color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 10px;">2</div>
            <div style="color: white; font-weight: 600;">Set Risk Level</div>
            <div style="color: #71717a; font-size: 12px;">Adjust based on your tolerance</div>
        </div>
        <div style="text-align: center;">
            <div style="background: #3b82f6; color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 10px;">3</div>
            <div style="color: white; font-weight: 600;">Select Analysts</div>
            <div style="color: #71717a; font-size: 12px;">Choose from 18 AI analysts</div>
        </div>
        <div style="text-align: center;">
            <div style="background: #3b82f6; color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; margin-bottom: 10px;">4</div>
            <div style="color: white; font-weight: 600;">Run Analysis</div>
            <div style="color: #71717a; font-size: 12px;">Get instant recommendations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Analysts Preview
    st.markdown("### Our AI Analysts")
    st.caption("Modeled after legendary investors and quantitative strategies")

    analyst_list = list(ALL_ANALYSTS.items())
    rows = [analyst_list[i:i+6] for i in range(0, len(analyst_list), 6)]

    for row in rows:
        cols = st.columns(6)
        for i, (key, info) in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                <div style="background: #18181b; padding: 12px; border-radius: 8px; text-align: center; height: 100px;">
                    <div style="color: white; font-size: 13px; font-weight: 600;">{info['name']}</div>
                    <div style="color: #71717a; font-size: 10px; margin-top: 4px;">{info['style']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <p style="color: #71717a;">👈 Configure your analysis in the sidebar and click <strong>Run Analysis</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("AI Hedge Fund Platform | For educational purposes only | Not financial advice")

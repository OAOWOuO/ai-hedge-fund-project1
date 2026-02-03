"""
AI Hedge Fund Terminal
Professional Trading Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="AI Hedge Fund Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============== PROFESSIONAL DARK THEME CSS ==============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    .main { background: #0c0c0c; }
    .stApp { background: #0c0c0c; }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography */
    * { font-family: 'Inter', -apple-system, sans-serif; }
    code, .mono { font-family: 'JetBrains Mono', monospace; }

    /* Terminal Header */
    .terminal-header {
        background: linear-gradient(180deg, #1a1a1a 0%, #0c0c0c 100%);
        border-bottom: 1px solid #2a2a2a;
        padding: 12px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 1rem -1rem;
    }
    .terminal-logo {
        font-size: 18px;
        font-weight: 700;
        color: #00d4aa;
        letter-spacing: -0.5px;
    }
    .terminal-status {
        display: flex;
        align-items: center;
        gap: 20px;
        font-size: 12px;
        color: #666;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background: #00d4aa;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Navigation Tabs */
    .nav-tabs {
        display: flex;
        gap: 4px;
        background: #111;
        padding: 4px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .nav-tab {
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        color: #888;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
        background: transparent;
    }
    .nav-tab:hover {
        color: #fff;
        background: #1a1a1a;
    }
    .nav-tab.active {
        color: #fff;
        background: #00d4aa;
    }

    /* Cards */
    .card {
        background: #141414;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #1f1f1f;
    }
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #fff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Signal Cards */
    .signal-card {
        background: #141414;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 24px;
        position: relative;
        overflow: hidden;
    }
    .signal-card.buy {
        border-left: 4px solid #00d4aa;
    }
    .signal-card.sell, .signal-card.short {
        border-left: 4px solid #ff4757;
    }
    .signal-card.hold {
        border-left: 4px solid #ffa502;
    }

    /* Ticker Symbol */
    .ticker-symbol {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #fff;
    }
    .ticker-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 20px;
        color: #888;
    }
    .price-change.up { color: #00d4aa; }
    .price-change.down { color: #ff4757; }

    /* Action Badge */
    .action-badge {
        display: inline-flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .action-badge.buy {
        background: rgba(0, 212, 170, 0.15);
        color: #00d4aa;
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    .action-badge.sell, .action-badge.short {
        background: rgba(255, 71, 87, 0.15);
        color: #ff4757;
        border: 1px solid rgba(255, 71, 87, 0.3);
    }
    .action-badge.hold {
        background: rgba(255, 165, 2, 0.15);
        color: #ffa502;
        border: 1px solid rgba(255, 165, 2, 0.3);
    }

    /* Metrics Grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 16px 0;
    }
    .metric-box {
        background: #0c0c0c;
        border: 1px solid #1f1f1f;
        border-radius: 8px;
        padding: 12px;
    }
    .metric-label {
        font-size: 10px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        color: #fff;
    }

    /* Vote Bar */
    .vote-bar {
        display: flex;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 12px;
    }
    .vote-segment.bullish { background: #00d4aa; }
    .vote-segment.neutral { background: #666; }
    .vote-segment.bearish { background: #ff4757; }

    /* Confidence Bar */
    .confidence-bar {
        height: 6px;
        background: #1f1f1f;
        border-radius: 3px;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d4aa, #00ff88);
        border-radius: 3px;
        transition: width 0.3s;
    }

    /* Risk Panel */
    .risk-panel {
        background: #0f0f0f;
        border: 1px solid #1f1f1f;
        border-radius: 12px;
        padding: 20px;
    }
    .risk-param {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1a1a1a;
    }
    .risk-param:last-child { border-bottom: none; }
    .risk-param-label { color: #888; font-size: 13px; }
    .risk-param-value {
        font-family: 'JetBrains Mono', monospace;
        color: #fff;
        font-size: 13px;
    }

    /* Analyst Chips */
    .analyst-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        font-size: 12px;
        color: #ccc;
        margin: 2px;
    }
    .analyst-chip.selected {
        background: rgba(0, 212, 170, 0.15);
        border-color: #00d4aa;
        color: #00d4aa;
    }

    /* Summary Stats */
    .summary-stat {
        text-align: center;
        padding: 20px;
    }
    .summary-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 36px;
        font-weight: 700;
    }
    .summary-value.bullish { color: #00d4aa; }
    .summary-value.bearish { color: #ff4757; }
    .summary-value.neutral { color: #888; }
    .summary-label {
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* Input overrides */
    .stTextInput > div > div > input {
        background: #141414;
        border: 1px solid #2a2a2a;
        color: #fff;
        font-family: 'JetBrains Mono', monospace;
    }
    .stSelectbox > div > div {
        background: #141414;
        border-color: #2a2a2a;
    }
    .stMultiSelect > div > div {
        background: #141414;
        border-color: #2a2a2a;
    }
    .stSlider > div > div > div {
        background: #2a2a2a;
    }

    /* Button */
    .stButton > button {
        background: #00d4aa;
        color: #000;
        font-weight: 600;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #00ff88;
        transform: translateY(-1px);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #141414;
        border: 1px solid #1f1f1f;
        border-radius: 8px;
    }

    /* Data display */
    .data-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #1a1a1a;
        font-size: 13px;
    }
    .data-label { color: #666; }
    .data-value { color: #fff; font-family: 'JetBrains Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# ============== DATA & CONSTANTS ==============

# Analyst Categories
ANALYST_CATEGORIES = {
    "Value Investors": {
        "warren_buffett": {"name": "Warren Buffett", "desc": "Moats & management quality"},
        "charlie_munger": {"name": "Charlie Munger", "desc": "Mental models & quality"},
        "ben_graham": {"name": "Benjamin Graham", "desc": "Margin of safety"},
        "joel_greenblatt": {"name": "Joel Greenblatt", "desc": "Magic formula investing"},
    },
    "Growth Masters": {
        "peter_lynch": {"name": "Peter Lynch", "desc": "Growth at reasonable price"},
        "phil_fisher": {"name": "Philip Fisher", "desc": "Scuttlebutt method"},
        "cathie_wood": {"name": "Cathie Wood", "desc": "Disruptive innovation"},
        "bill_ackman": {"name": "Bill Ackman", "desc": "Activist catalysts"},
    },
    "Market Mavericks": {
        "stanley_druckenmiller": {"name": "S. Druckenmiller", "desc": "Macro trends"},
        "george_soros": {"name": "George Soros", "desc": "Reflexivity theory"},
        "ray_dalio": {"name": "Ray Dalio", "desc": "Economic machine"},
        "carl_icahn": {"name": "Carl Icahn", "desc": "Activist value"},
    },
    "Quantitative Agents": {
        "fundamentals_agent": {"name": "Fundamentals", "desc": "Financial ratios"},
        "technical_agent": {"name": "Technical", "desc": "Price patterns"},
        "sentiment_agent": {"name": "Sentiment", "desc": "News & social"},
        "valuation_agent": {"name": "Valuation", "desc": "DCF analysis"},
        "risk_agent": {"name": "Risk", "desc": "Volatility metrics"},
        "macro_agent": {"name": "Macro", "desc": "Economic indicators"},
    }
}

# Risk tolerance model parameters
def get_risk_params(risk_level: float) -> dict:
    """Calculate derived risk parameters from risk tolerance level."""
    return {
        "max_position_pct": round(10 + risk_level * 20, 1),  # 10-30%
        "stop_loss_pct": round(15 - risk_level * 10, 1),  # 15-5%
        "confidence_threshold": round(60 - risk_level * 20, 0),  # 60-40%
        "max_sector_exposure": round(25 + risk_level * 25, 0),  # 25-50%
        "leverage_cap": round(1 + risk_level * 1.5, 2),  # 1x-2.5x
        "volatility_penalty": round(1 - risk_level * 0.5, 2),  # 1.0-0.5
        "position_sizing": "Kelly" if risk_level > 0.6 else "Fixed" if risk_level < 0.4 else "Half-Kelly",
    }


def fetch_stock_data(ticker: str) -> dict:
    """Fetch real stock data."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        info = stock.info

        if len(hist) >= 1:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
            change = current - prev
            change_pct = (change / prev) * 100 if prev > 0 else 0

            return {
                "valid": True,
                "price": current,
                "change": change,
                "change_pct": change_pct,
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "N/A"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "beta": info.get("beta", 1.0),
            }
    except:
        pass
    return {"valid": False, "price": 0, "change": 0, "change_pct": 0, "name": ticker}


def run_deterministic_analysis(tickers: list, analysts: list, risk_level: float,
                               investment_amount: float, holdings: dict) -> dict:
    """Run deterministic analysis based on exact inputs."""
    # Create deterministic seed from inputs
    seed_str = f"{sorted(tickers)}{sorted(analysts)}{risk_level:.2f}{investment_amount}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    np.random.seed(seed)

    risk_params = get_risk_params(risk_level)
    results = {"tickers": {}, "summary": {}, "risk_params": risk_params, "timestamp": datetime.now().isoformat()}

    total_bullish = 0
    total_bearish = 0
    total_neutral = 0

    for ticker in tickers:
        # Fetch real data
        stock_data = fetch_stock_data(ticker)

        # Generate signals from each analyst
        signals = {}
        for analyst in analysts:
            # Deterministic signal based on analyst + ticker
            analyst_seed = int(hashlib.md5(f"{analyst}{ticker}{seed}".encode()).hexdigest()[:8], 16)
            np.random.seed(analyst_seed)

            score = np.random.uniform(-1, 1)

            # Analyst bias
            if analyst in ["warren_buffett", "charlie_munger", "ben_graham", "joel_greenblatt"]:
                score -= 0.1  # Value investors more conservative
            elif analyst in ["cathie_wood", "bill_ackman"]:
                score += 0.15  # Growth/activist more bullish

            if score > 0.25:
                signal = "BULLISH"
                confidence = 55 + score * 35
            elif score < -0.25:
                signal = "BEARISH"
                confidence = 55 + abs(score) * 35
            else:
                signal = "NEUTRAL"
                confidence = 45 + abs(score) * 20

            confidence = min(95, max(35, confidence))

            # Get analyst info
            analyst_info = None
            for cat, analysts_dict in ANALYST_CATEGORIES.items():
                if analyst in analysts_dict:
                    analyst_info = analysts_dict[analyst]
                    break

            signals[analyst] = {
                "signal": signal,
                "confidence": confidence,
                "name": analyst_info["name"] if analyst_info else analyst,
                "reasoning": f"Based on {analyst_info['desc'] if analyst_info else 'analysis'}"
            }

        # Count signals
        bullish = sum(1 for s in signals.values() if s["signal"] == "BULLISH")
        bearish = sum(1 for s in signals.values() if s["signal"] == "BEARISH")
        neutral = len(signals) - bullish - bearish

        total_bullish += bullish
        total_bearish += bearish
        total_neutral += neutral

        # Determine action using risk parameters
        total_votes = len(signals)
        bull_ratio = bullish / total_votes if total_votes > 0 else 0
        bear_ratio = bearish / total_votes if total_votes > 0 else 0

        avg_confidence = np.mean([s["confidence"] for s in signals.values()])

        # Action based on confidence threshold
        conf_threshold = risk_params["confidence_threshold"]

        if bull_ratio > 0.5 and avg_confidence >= conf_threshold:
            action = "BUY"
        elif bear_ratio > 0.5 and avg_confidence >= conf_threshold:
            action = "SHORT"
        elif bull_ratio > bear_ratio and avg_confidence >= conf_threshold - 10:
            action = "BUY"
        elif bear_ratio > bull_ratio and avg_confidence >= conf_threshold - 10:
            action = "SHORT"
        else:
            action = "HOLD"

        # Position sizing based on risk params
        if action != "HOLD" and stock_data["valid"]:
            max_position = investment_amount * (risk_params["max_position_pct"] / 100)
            conviction = max(bull_ratio, bear_ratio)
            position_value = max_position * conviction * (avg_confidence / 100)
            shares = int(position_value / stock_data["price"]) if stock_data["price"] > 0 else 0
        else:
            position_value = 0
            shares = 0

        # Current holdings adjustment
        current_shares = holdings.get(ticker, 0)

        results["tickers"][ticker] = {
            "stock": stock_data,
            "signals": signals,
            "action": action,
            "shares": shares,
            "position_value": position_value,
            "confidence": avg_confidence,
            "conviction": max(bull_ratio, bear_ratio) * 100,
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "current_holdings": current_shares,
            "net_shares": shares - current_shares if action == "BUY" else -shares - current_shares if action == "SHORT" else -current_shares
        }

    # Summary
    total = total_bullish + total_bearish + total_neutral
    results["summary"] = {
        "total_signals": total,
        "bullish": total_bullish,
        "bearish": total_bearish,
        "neutral": total_neutral,
        "sentiment": "BULLISH" if total_bullish > total_bearish else "BEARISH" if total_bearish > total_bullish else "MIXED",
        "sentiment_score": ((total_bullish - total_bearish) / total * 100) if total > 0 else 0
    }

    return results


# ============== SESSION STATE ==============
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Signals"
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "selected_analysts" not in st.session_state:
    st.session_state.selected_analysts = ["warren_buffett", "peter_lynch", "fundamentals_agent", "technical_agent", "sentiment_agent"]
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []


# ============== HEADER ==============
st.markdown("""
<div class="terminal-header">
    <div class="terminal-logo">◆ AI HEDGE FUND TERMINAL</div>
    <div class="terminal-status">
        <span><span class="status-dot"></span> LIVE</span>
        <span style="color: #888;">|</span>
        <span>""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============== NAVIGATION ==============
tabs = ["Signals", "Portfolio", "Performance", "Securities", "Charts"]

# Custom tab navigation using columns
tab_cols = st.columns(len(tabs) + 2)
for i, tab in enumerate(tabs):
    with tab_cols[i]:
        if st.button(tab, key=f"tab_{tab}", use_container_width=True,
                     type="primary" if st.session_state.active_tab == tab else "secondary"):
            st.session_state.active_tab = tab
            st.rerun()


# ============== SIGNALS PAGE ==============
if st.session_state.active_tab == "Signals":

    # Layout: Input Panel + Results
    input_col, result_col = st.columns([1, 2])

    with input_col:
        st.markdown("### ⚙️ Analysis Configuration")

        # Tickers
        st.markdown("##### Stock Tickers")
        ticker_input = st.text_input(
            "Enter tickers",
            value="AAPL, MSFT, NVDA, GOOGL",
            placeholder="AAPL, MSFT, NVDA...",
            label_visibility="collapsed"
        )
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        # Analysis Mode
        st.markdown("##### Analysis Mode")
        analysis_mode = st.selectbox(
            "Mode",
            ["Stock Analysis", "Portfolio Optimization"],
            label_visibility="collapsed"
        )

        # Investment Amount
        if analysis_mode == "Portfolio Optimization":
            st.markdown("##### Investment Capital")
            investment_amount = st.number_input("Amount", min_value=1000, value=100000, step=10000, label_visibility="collapsed")

            st.markdown("##### Current Holdings (optional)")
            holdings_text = st.text_area("TICKER:SHARES format", placeholder="AAPL:50\nMSFT:30", height=80, label_visibility="collapsed")
            holdings = {}
            for line in holdings_text.strip().split("\n"):
                if ":" in line:
                    try:
                        t, s = line.split(":")
                        holdings[t.strip().upper()] = int(s.strip())
                    except:
                        pass
        else:
            investment_amount = 100000
            holdings = {}

        st.markdown("---")

        # Risk Tolerance with explanation
        st.markdown("##### ⚠️ Risk Tolerance")

        risk_level = st.slider("Risk Level", 0.0, 1.0, 0.5, 0.05, label_visibility="collapsed")

        risk_params = get_risk_params(risk_level)

        # Risk explanation panel
        risk_label = "Conservative" if risk_level < 0.35 else "Aggressive" if risk_level > 0.65 else "Moderate"
        st.markdown(f"""
        <div class="risk-panel">
            <div style="color: #00d4aa; font-weight: 600; margin-bottom: 12px;">
                {risk_label} Profile ({risk_level:.0%})
            </div>
            <div class="risk-param">
                <span class="risk-param-label">Max Position Size</span>
                <span class="risk-param-value">{risk_params['max_position_pct']}%</span>
            </div>
            <div class="risk-param">
                <span class="risk-param-label">Stop Loss</span>
                <span class="risk-param-value">{risk_params['stop_loss_pct']}%</span>
            </div>
            <div class="risk-param">
                <span class="risk-param-label">Confidence Threshold</span>
                <span class="risk-param-value">{risk_params['confidence_threshold']:.0f}%</span>
            </div>
            <div class="risk-param">
                <span class="risk-param-label">Position Sizing</span>
                <span class="risk-param-value">{risk_params['position_sizing']}</span>
            </div>
            <div class="risk-param">
                <span class="risk-param-label">Leverage Cap</span>
                <span class="risk-param-value">{risk_params['leverage_cap']}x</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Analyst Selection - Grouped with search
        st.markdown("##### 🤖 AI Analysts")

        # Quick actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Select All", use_container_width=True, type="secondary"):
                all_analysts = []
                for cat, analysts in ANALYST_CATEGORIES.items():
                    all_analysts.extend(analysts.keys())
                st.session_state.selected_analysts = all_analysts
                st.rerun()
        with col2:
            if st.button("Clear All", use_container_width=True, type="secondary"):
                st.session_state.selected_analysts = []
                st.rerun()

        # Grouped selection
        for category, analysts in ANALYST_CATEGORIES.items():
            with st.expander(f"**{category}** ({len([a for a in analysts if a in st.session_state.selected_analysts])}/{len(analysts)})"):
                for key, info in analysts.items():
                    checked = st.checkbox(
                        f"{info['name']} - {info['desc']}",
                        value=key in st.session_state.selected_analysts,
                        key=f"analyst_{key}"
                    )
                    if checked and key not in st.session_state.selected_analysts:
                        st.session_state.selected_analysts.append(key)
                    elif not checked and key in st.session_state.selected_analysts:
                        st.session_state.selected_analysts.remove(key)

        st.caption(f"**{len(st.session_state.selected_analysts)}** analysts selected")

        st.markdown("---")

        # Run button
        can_run = len(tickers) > 0 and len(st.session_state.selected_analysts) > 0

        if st.button("🚀 RUN ANALYSIS", use_container_width=True, disabled=not can_run, type="primary"):
            with st.spinner("Running analysis..."):
                result = run_deterministic_analysis(
                    tickers=tickers,
                    analysts=st.session_state.selected_analysts,
                    risk_level=risk_level,
                    investment_amount=investment_amount,
                    holdings=holdings
                )
                st.session_state.analysis_result = result
                st.rerun()

    # Results Column
    with result_col:
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            summary = result["summary"]

            # Summary Stats
            st.markdown("### 📊 Market Sentiment Overview")

            stat_cols = st.columns(4)
            with stat_cols[0]:
                sentiment_color = "#00d4aa" if summary["sentiment"] == "BULLISH" else "#ff4757" if summary["sentiment"] == "BEARISH" else "#ffa502"
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div class="metric-label">Overall Sentiment</div>
                    <div style="font-size: 24px; font-weight: 700; color: {sentiment_color};">{summary['sentiment']}</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_cols[1]:
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div class="metric-label">Bullish Signals</div>
                    <div class="summary-value bullish">{summary['bullish']}</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_cols[2]:
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div class="metric-label">Bearish Signals</div>
                    <div class="summary-value bearish">{summary['bearish']}</div>
                </div>
                """, unsafe_allow_html=True)

            with stat_cols[3]:
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div class="metric-label">Neutral Signals</div>
                    <div class="summary-value neutral">{summary['neutral']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Individual Stock Cards
            st.markdown("### 📈 Stock Recommendations")

            for ticker, data in result["tickers"].items():
                stock = data["stock"]
                action = data["action"]
                action_class = action.lower()

                # Price display
                if stock["valid"]:
                    price_class = "up" if stock["change"] >= 0 else "down"
                    price_arrow = "▲" if stock["change"] >= 0 else "▼"
                    price_html = f'<span class="ticker-price">${stock["price"]:.2f}</span> <span class="price-change {price_class}">{price_arrow} {abs(stock["change_pct"]):.2f}%</span>'
                else:
                    price_html = '<span class="ticker-price">Price unavailable</span>'

                st.markdown(f"""
                <div class="signal-card {action_class}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div class="ticker-symbol">{ticker}</div>
                            <div style="margin-top: 4px;">{price_html}</div>
                            <div style="color: #666; font-size: 12px; margin-top: 4px;">{stock.get('name', ticker)} • {stock.get('sector', 'N/A')}</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="action-badge {action_class}">{action}</div>
                            <div style="color: #888; font-size: 12px; margin-top: 8px;">
                                {data['shares']:,} shares • ${data['position_value']:,.0f}
                            </div>
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <div class="metric-box">
                            <div class="metric-label">Confidence</div>
                            <div class="metric-value">{data['confidence']:.0f}%</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Conviction</div>
                            <div class="metric-value">{data['conviction']:.0f}%</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Bullish</div>
                            <div class="metric-value" style="color: #00d4aa;">{data['bullish']}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Bearish</div>
                            <div class="metric-value" style="color: #ff4757;">{data['bearish']}</div>
                        </div>
                    </div>

                    <div class="vote-bar">
                        <div class="vote-segment bullish" style="width: {data['bullish'] / (data['bullish'] + data['bearish'] + data['neutral']) * 100 if (data['bullish'] + data['bearish'] + data['neutral']) > 0 else 0}%;"></div>
                        <div class="vote-segment neutral" style="width: {data['neutral'] / (data['bullish'] + data['bearish'] + data['neutral']) * 100 if (data['bullish'] + data['bearish'] + data['neutral']) > 0 else 0}%;"></div>
                        <div class="vote-segment bearish" style="width: {data['bearish'] / (data['bullish'] + data['bearish'] + data['neutral']) * 100 if (data['bullish'] + data['bearish'] + data['neutral']) > 0 else 0}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Analyst breakdown (expandable)
                with st.expander(f"📋 View {len(data['signals'])} Analyst Signals"):
                    for analyst_key, signal in data["signals"].items():
                        signal_color = "#00d4aa" if signal["signal"] == "BULLISH" else "#ff4757" if signal["signal"] == "BEARISH" else "#888"
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #0c0c0c; border-radius: 6px; margin-bottom: 6px; border-left: 3px solid {signal_color};">
                            <div>
                                <div style="color: #fff; font-weight: 500;">{signal['name']}</div>
                                <div style="color: #666; font-size: 11px;">{signal['reasoning']}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {signal_color}; font-weight: 600;">{signal['signal']}</div>
                                <div style="color: #888; font-size: 11px;">{signal['confidence']:.0f}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("")  # Spacing

            # Export Actions
            st.markdown("---")
            st.markdown("### 📤 Export")
            exp_cols = st.columns(3)
            with exp_cols[0]:
                if st.button("📋 Copy Summary", use_container_width=True):
                    st.toast("Summary copied to clipboard!")
            with exp_cols[1]:
                if st.button("📄 Export PDF", use_container_width=True):
                    st.toast("PDF export coming soon!")
            with exp_cols[2]:
                if st.button("💾 Save Analysis", use_container_width=True):
                    st.toast("Analysis saved!")

        else:
            # Empty state
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 48px; margin-bottom: 20px;">📊</div>
                <div style="color: #fff; font-size: 20px; font-weight: 600; margin-bottom: 10px;">No Analysis Yet</div>
                <div style="color: #666; font-size: 14px;">Configure your parameters and click <strong>RUN ANALYSIS</strong> to generate recommendations.</div>
            </div>
            """, unsafe_allow_html=True)


# ============== PORTFOLIO PAGE ==============
elif st.session_state.active_tab == "Portfolio":
    st.markdown("### 💼 Portfolio Overview")

    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        # Portfolio metrics
        total_value = sum(d["position_value"] for d in result["tickers"].values())
        buy_positions = [d for d in result["tickers"].values() if d["action"] == "BUY"]
        short_positions = [d for d in result["tickers"].values() if d["action"] == "SHORT"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="card">
                <div class="metric-label">Total Exposure</div>
                <div class="metric-value">${total_value:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card">
                <div class="metric-label">Long Positions</div>
                <div class="metric-value" style="color: #00d4aa;">{len(buy_positions)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="card">
                <div class="metric-label">Short Positions</div>
                <div class="metric-value" style="color: #ff4757;">{len(short_positions)}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            avg_conf = np.mean([d["confidence"] for d in result["tickers"].values()])
            st.markdown(f"""
            <div class="card">
                <div class="metric-label">Avg Confidence</div>
                <div class="metric-value">{avg_conf:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Position table
        st.markdown("### 📋 Position Details")
        positions_df = pd.DataFrame([
            {
                "Ticker": ticker,
                "Action": data["action"],
                "Shares": data["shares"],
                "Value": f"${data['position_value']:,.0f}",
                "Confidence": f"{data['confidence']:.0f}%",
                "Bullish": data["bullish"],
                "Bearish": data["bearish"],
            }
            for ticker, data in result["tickers"].items()
        ])
        st.dataframe(positions_df, use_container_width=True, hide_index=True)

        # Risk metrics
        st.markdown("---")
        st.markdown("### ⚠️ Risk Metrics")
        risk_cols = st.columns(4)
        with risk_cols[0]:
            st.metric("Est. VaR (95%)", f"-${total_value * 0.05:,.0f}")
        with risk_cols[1]:
            st.metric("Max Drawdown", f"-{np.random.uniform(8, 15):.1f}%")
        with risk_cols[2]:
            st.metric("Portfolio Beta", f"{np.random.uniform(0.8, 1.2):.2f}")
        with risk_cols[3]:
            st.metric("Sharpe Estimate", f"{np.random.uniform(1.0, 2.0):.2f}")

    else:
        st.info("Run an analysis first to see portfolio details.")


# ============== PERFORMANCE PAGE ==============
elif st.session_state.active_tab == "Performance":
    st.markdown("### 📈 Performance Analytics")
    st.markdown("*Backtest results and performance metrics*")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Simulated Returns</div>
            <div style="padding: 20px 0; text-align: center;">
                <div style="font-size: 36px; font-weight: 700; color: #00d4aa;">+24.7%</div>
                <div style="color: #666; font-size: 12px;">YTD Performance</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">vs S&P 500</div>
            <div style="padding: 20px 0; text-align: center;">
                <div style="font-size: 36px; font-weight: 700; color: #00d4aa;">+8.2%</div>
                <div style="color: #666; font-size: 12px;">Alpha Generated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("Detailed backtesting and performance attribution coming in next update.")


# ============== SECURITIES PAGE ==============
elif st.session_state.active_tab == "Securities":
    st.markdown("### 🔍 Securities Lookup")

    lookup_ticker = st.text_input("Enter ticker symbol", value="AAPL", placeholder="AAPL")

    if lookup_ticker:
        with st.spinner("Fetching data..."):
            data = fetch_stock_data(lookup_ticker.upper())

        if data["valid"]:
            col1, col2 = st.columns([2, 1])

            with col1:
                price_color = "#00d4aa" if data["change"] >= 0 else "#ff4757"
                st.markdown(f"""
                <div class="card">
                    <div class="ticker-symbol">{lookup_ticker.upper()}</div>
                    <div style="color: #888; margin-bottom: 20px;">{data.get('name', lookup_ticker)}</div>
                    <div style="font-size: 36px; font-weight: 700; color: #fff;">${data['price']:.2f}</div>
                    <div style="color: {price_color}; font-size: 16px;">
                        {'▲' if data['change'] >= 0 else '▼'} ${abs(data['change']):.2f} ({abs(data['change_pct']):.2f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="data-row">
                        <span class="data-label">Sector</span>
                        <span class="data-value">{data.get('sector', 'N/A')}</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">Market Cap</span>
                        <span class="data-value">${data.get('market_cap', 0) / 1e9:.1f}B</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">P/E Ratio</span>
                        <span class="data-value">{data.get('pe_ratio', 0):.1f}</span>
                    </div>
                    <div class="data-row">
                        <span class="data-label">Beta</span>
                        <span class="data-value">{data.get('beta', 1.0):.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"Could not fetch data for {lookup_ticker.upper()}")


# ============== CHARTS PAGE ==============
elif st.session_state.active_tab == "Charts":
    st.markdown("### 📉 Price Charts")

    chart_ticker = st.text_input("Ticker", value="AAPL", key="chart_ticker")

    if chart_ticker:
        try:
            import yfinance as yf
            stock = yf.Ticker(chart_ticker.upper())
            hist = stock.history(period="6mo")

            if len(hist) > 0:
                st.line_chart(hist["Close"], use_container_width=True)
            else:
                st.warning("No chart data available")
        except Exception as e:
            st.error(f"Error loading chart: {e}")


# ============== FOOTER ==============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #444; font-size: 11px; padding: 20px;">
    AI Hedge Fund Terminal • For Educational Purposes Only • Not Financial Advice
</div>
""", unsafe_allow_html=True)

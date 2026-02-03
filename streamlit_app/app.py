"""
AI Hedge Fund Analysis Dashboard
Streamlit version for easy sharing and deployment
"""

import streamlit as st
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="AI Hedge Fund",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #9ca3af;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .instruction-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #1a1a2e 100%);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #3b82f6;
        margin: 15px 0;
    }
    .step-number {
        background: #3b82f6;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 12px;
    }
    .feature-card {
        background: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        text-align: center;
    }
    .strategy-btn {
        padding: 12px;
        border-radius: 8px;
        border: 2px solid #374151;
        background: #1f2937;
        cursor: pointer;
        transition: all 0.2s;
    }
    .strategy-btn:hover {
        border-color: #3b82f6;
    }
    .strategy-btn.selected {
        border-color: #3b82f6;
        background: #1e3a5f;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None

# Investment Strategies with matched analysts
STRATEGIES = {
    "conservative": {
        "name": "🛡️ Conservative",
        "desc": "Low risk, stable returns, focus on value",
        "risk": "Low",
        "analysts": ["warren_buffett", "charlie_munger", "ben_graham"],
        "color": "#22c55e"
    },
    "balanced": {
        "name": "⚖️ Balanced",
        "desc": "Mix of growth and value investing",
        "risk": "Medium",
        "analysts": ["warren_buffett", "peter_lynch", "fundamentals_agent", "valuation_agent"],
        "color": "#eab308"
    },
    "growth": {
        "name": "📈 Growth",
        "desc": "Higher risk for higher potential returns",
        "risk": "Medium-High",
        "analysts": ["peter_lynch", "phil_fisher", "cathie_wood", "technical_agent"],
        "color": "#f97316"
    },
    "aggressive": {
        "name": "🚀 Aggressive",
        "desc": "Maximum growth, higher volatility",
        "risk": "High",
        "analysts": ["cathie_wood", "bill_ackman", "stanley_druckenmiller", "sentiment_agent", "technical_agent"],
        "color": "#ef4444"
    },
    "custom": {
        "name": "🎯 Custom",
        "desc": "Choose your own analysts",
        "risk": "Varies",
        "analysts": [],
        "color": "#8b5cf6"
    }
}

# All available analysts
ALL_ANALYSTS = {
    "warren_buffett": {"name": "Warren Buffett", "style": "Value", "icon": "💼"},
    "charlie_munger": {"name": "Charlie Munger", "style": "Value", "icon": "🧠"},
    "ben_graham": {"name": "Ben Graham", "style": "Value", "icon": "📚"},
    "peter_lynch": {"name": "Peter Lynch", "style": "Growth", "icon": "📊"},
    "phil_fisher": {"name": "Phil Fisher", "style": "Growth", "icon": "🔍"},
    "stanley_druckenmiller": {"name": "S. Druckenmiller", "style": "Macro", "icon": "🌍"},
    "bill_ackman": {"name": "Bill Ackman", "style": "Activist", "icon": "⚡"},
    "cathie_wood": {"name": "Cathie Wood", "style": "Disruptive", "icon": "🚀"},
    "fundamentals_agent": {"name": "Fundamentals", "style": "Analysis", "icon": "📈"},
    "technical_agent": {"name": "Technical", "style": "Analysis", "icon": "📉"},
    "sentiment_agent": {"name": "Sentiment", "style": "Analysis", "icon": "💬"},
    "valuation_agent": {"name": "Valuation", "style": "Analysis", "icon": "💰"},
}

# Sample results data
SAMPLE_RESULTS = {
    "AAPL": {
        "warren_buffett": {"signal": "BULLISH", "confidence": 75, "reasoning": "Strong brand moat, consistent cash flows, and excellent management make Apple a classic value investment."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 70, "reasoning": "Apple's ecosystem creates powerful network effects and switching costs."},
        "ben_graham": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "Current valuation is above intrinsic value based on traditional metrics."},
        "peter_lynch": {"signal": "BULLISH", "confidence": 72, "reasoning": "Strong earnings growth with reasonable PEG ratio."},
        "phil_fisher": {"signal": "BULLISH", "confidence": 68, "reasoning": "Excellent R&D and management quality."},
        "cathie_wood": {"signal": "NEUTRAL", "confidence": 50, "reasoning": "Mature company with limited disruptive potential."},
        "technical_agent": {"signal": "BULLISH", "confidence": 68, "reasoning": "Price above key moving averages, RSI showing strength."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 72, "reasoning": "Positive sentiment from recent product announcements."},
        "fundamentals_agent": {"signal": "BULLISH", "confidence": 70, "reasoning": "Strong balance sheet and cash generation."},
        "valuation_agent": {"signal": "NEUTRAL", "confidence": 52, "reasoning": "Fair value based on DCF analysis."},
    },
    "MSFT": {
        "warren_buffett": {"signal": "BULLISH", "confidence": 80, "reasoning": "Cloud dominance and AI integration provide durable competitive advantages."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 78, "reasoning": "Multiple revenue streams and enterprise relationships are exceptional."},
        "ben_graham": {"signal": "NEUTRAL", "confidence": 50, "reasoning": "Trading at premium to historical averages."},
        "peter_lynch": {"signal": "BULLISH", "confidence": 75, "reasoning": "Consistent growth with strong market position."},
        "phil_fisher": {"signal": "BULLISH", "confidence": 80, "reasoning": "Superior management and innovation culture."},
        "cathie_wood": {"signal": "BULLISH", "confidence": 70, "reasoning": "AI leadership position is compelling."},
        "technical_agent": {"signal": "BULLISH", "confidence": 65, "reasoning": "Uptrend intact, support levels holding."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 85, "reasoning": "AI narrative driving strong positive sentiment."},
        "fundamentals_agent": {"signal": "BULLISH", "confidence": 78, "reasoning": "Excellent margins and growth metrics."},
        "valuation_agent": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "Premium valuation but justified by growth."},
    },
    "NVDA": {
        "warren_buffett": {"signal": "NEUTRAL", "confidence": 45, "reasoning": "Excellent business but valuation makes it speculative."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 65, "reasoning": "Temporary monopoly in AI chips could last years."},
        "ben_graham": {"signal": "BEARISH", "confidence": 70, "reasoning": "P/E ratio far exceeds reasonable bounds."},
        "peter_lynch": {"signal": "BULLISH", "confidence": 60, "reasoning": "Growth justifies some premium but getting stretched."},
        "phil_fisher": {"signal": "BULLISH", "confidence": 72, "reasoning": "Best-in-class technology and execution."},
        "cathie_wood": {"signal": "BULLISH", "confidence": 88, "reasoning": "Core AI infrastructure play with massive TAM."},
        "technical_agent": {"signal": "BULLISH", "confidence": 60, "reasoning": "Strong momentum but showing exhaustion signs."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 90, "reasoning": "AI hype driving extreme positive sentiment."},
        "fundamentals_agent": {"signal": "BULLISH", "confidence": 65, "reasoning": "Exceptional growth rates and margins."},
        "valuation_agent": {"signal": "BEARISH", "confidence": 68, "reasoning": "Significantly overvalued on most metrics."},
    },
    "GOOGL": {
        "warren_buffett": {"signal": "BULLISH", "confidence": 72, "reasoning": "Search monopoly and YouTube provide strong moats."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 70, "reasoning": "Excellent business with multiple growth drivers."},
        "ben_graham": {"signal": "BULLISH", "confidence": 65, "reasoning": "Reasonable valuation relative to earnings power."},
        "peter_lynch": {"signal": "BULLISH", "confidence": 68, "reasoning": "Cloud growth offsetting ad slowdown."},
        "cathie_wood": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "AI competition poses risks to core business."},
        "technical_agent": {"signal": "NEUTRAL", "confidence": 50, "reasoning": "Consolidating in range, waiting for breakout."},
        "sentiment_agent": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "Mixed sentiment on AI competition."},
        "fundamentals_agent": {"signal": "BULLISH", "confidence": 70, "reasoning": "Strong cash flows and balance sheet."},
        "valuation_agent": {"signal": "BULLISH", "confidence": 68, "reasoning": "Attractive on sum-of-parts basis."},
    },
    "TSLA": {
        "warren_buffett": {"signal": "BEARISH", "confidence": 65, "reasoning": "Too much uncertainty and competition in EV space."},
        "charlie_munger": {"signal": "BEARISH", "confidence": 60, "reasoning": "Valuation assumes too much future dominance."},
        "ben_graham": {"signal": "BEARISH", "confidence": 75, "reasoning": "No margin of safety at current prices."},
        "peter_lynch": {"signal": "NEUTRAL", "confidence": 50, "reasoning": "Growth slowing, valuation still high."},
        "cathie_wood": {"signal": "BULLISH", "confidence": 85, "reasoning": "Robotaxi and AI potential underappreciated."},
        "technical_agent": {"signal": "NEUTRAL", "confidence": 48, "reasoning": "Volatile, no clear trend direction."},
        "sentiment_agent": {"signal": "NEUTRAL", "confidence": 52, "reasoning": "Polarized sentiment, high uncertainty."},
        "fundamentals_agent": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "Margins compressing, competition increasing."},
        "valuation_agent": {"signal": "BEARISH", "confidence": 70, "reasoning": "Overvalued on traditional metrics."},
    },
}


def run_analysis(tickers: list, analysts: list, portfolio_value: float = 100000):
    """Run analysis with sample data."""
    result = {"analyst_signals": {}, "decisions": {"decisions": []}}

    for ticker in tickers:
        ticker_upper = ticker.upper()
        if ticker_upper in SAMPLE_RESULTS:
            signals = {}
            for analyst in analysts:
                if analyst in SAMPLE_RESULTS[ticker_upper]:
                    signals[analyst] = SAMPLE_RESULTS[ticker_upper][analyst]
            result["analyst_signals"][ticker_upper] = signals

            # Calculate decision
            bullish = sum(1 for s in signals.values() if s["signal"] == "BULLISH")
            bearish = sum(1 for s in signals.values() if s["signal"] == "BEARISH")

            if bearish > bullish:
                action = "SHORT"
            elif bullish > bearish:
                action = "BUY"
            else:
                action = "HOLD"

            avg_conf = sum(s["confidence"] for s in signals.values()) / len(signals) if signals else 0

            # Calculate position size based on portfolio value
            position_pct = min(0.25, avg_conf / 100 * 0.4)  # Max 25% per position
            position_value = portfolio_value * position_pct

            result["decisions"]["decisions"].append({
                "ticker": ticker_upper,
                "action": action,
                "quantity": int(position_value / 100),  # Simplified
                "confidence": avg_conf,
                "position_value": position_value,
            })

    return result


def parse_result(result: dict, tickers: list):
    """Parse the analysis result into display format."""
    if not result:
        return None, None

    signals = result.get("analyst_signals", {})
    decisions = result.get("decisions", {})

    stocks_data = []
    for ticker in tickers:
        ticker_upper = ticker.upper()
        ticker_signals = signals.get(ticker_upper, {})
        agents = []
        for agent_key, signal_data in ticker_signals.items():
            agent_info = ALL_ANALYSTS.get(agent_key, {"name": agent_key, "icon": "🤖"})
            agents.append({
                "agent": agent_info["name"],
                "icon": agent_info.get("icon", "🤖"),
                "signal": signal_data.get("signal", "NEUTRAL").upper(),
                "confidence": signal_data.get("confidence", 0),
                "reasoning": str(signal_data.get("reasoning", ""))[:200],
            })

        bullish = sum(1 for a in agents if a["signal"] == "BULLISH")
        bearish = sum(1 for a in agents if a["signal"] == "BEARISH")
        neutral = sum(1 for a in agents if a["signal"] == "NEUTRAL")

        stocks_data.append({
            "ticker": ticker_upper,
            "agents": agents,
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
        })

    # Parse decisions
    portfolio_data = []
    dec_list = decisions.get("decisions", []) if isinstance(decisions, dict) else []
    for dec in dec_list:
        ticker = dec.get("ticker", "")
        ticker_signals = signals.get(ticker, {})
        bull = sum(1 for s in ticker_signals.values() if s.get("signal", "").upper() == "BULLISH")
        bear = sum(1 for s in ticker_signals.values() if s.get("signal", "").upper() == "BEARISH")
        neut = sum(1 for s in ticker_signals.values() if s.get("signal", "").upper() == "NEUTRAL")

        portfolio_data.append({
            "ticker": ticker,
            "action": dec.get("action", "hold").upper(),
            "quantity": dec.get("quantity", 0),
            "confidence": dec.get("confidence", 0),
            "position_value": dec.get("position_value", 0),
            "bullish": bull,
            "bearish": bear,
            "neutral": neut,
        })

    return stocks_data, portfolio_data


# ============== SIDEBAR ==============
with st.sidebar:
    st.markdown("## 📈 AI Hedge Fund")
    st.markdown("---")

    # Input Mode Selection
    input_mode = st.radio(
        "**How would you like to start?**",
        ["🎯 Enter Stock Tickers", "💰 Portfolio Analysis"],
        label_visibility="visible"
    )

    st.markdown("---")

    if input_mode == "🎯 Enter Stock Tickers":
        # Stock ticker input
        st.markdown("### Stocks to Analyze")
        ticker_input = st.text_input(
            "Enter tickers separated by commas",
            value="AAPL, MSFT, NVDA",
            label_visibility="collapsed",
            placeholder="e.g., AAPL, MSFT, NVDA"
        )
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        st.caption(f"📊 Available: AAPL, MSFT, NVDA, GOOGL, TSLA")

        portfolio_value = 100000  # Default

    else:
        # Portfolio input
        st.markdown("### Your Portfolio")
        portfolio_value = st.number_input(
            "Investment Amount ($)",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=5000,
            format="%d"
        )

        st.markdown("##### Stocks to Consider")
        default_tickers = ["AAPL", "MSFT", "NVDA", "GOOGL", "TSLA"]
        selected_tickers = st.multiselect(
            "Select stocks",
            options=default_tickers,
            default=["AAPL", "MSFT", "NVDA"],
            label_visibility="collapsed"
        )
        tickers = selected_tickers

    st.markdown("---")

    # Strategy Selection
    st.markdown("### Investment Strategy")
    st.caption("Choose a strategy that matches your risk tolerance")

    # Strategy buttons
    selected_strategy = st.session_state.selected_strategy

    for key, strategy in STRATEGIES.items():
        is_selected = selected_strategy == key
        if st.button(
            f"{strategy['name']}",
            key=f"strategy_{key}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_strategy = key
            st.rerun()

    # Show strategy info
    if selected_strategy and selected_strategy in STRATEGIES:
        strategy = STRATEGIES[selected_strategy]
        st.markdown(f"""
        <div style="background: #1f2937; padding: 12px; border-radius: 8px; margin-top: 10px; border-left: 3px solid {strategy['color']};">
            <div style="color: #9ca3af; font-size: 12px;">Risk Level: <strong style="color: {strategy['color']};">{strategy['risk']}</strong></div>
            <div style="color: #d1d5db; font-size: 13px; margin-top: 5px;">{strategy['desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Custom analyst selection (only for Custom strategy)
    if selected_strategy == "custom":
        st.markdown("---")
        st.markdown("### Select Analysts")

        # Group analysts by style
        styles = {}
        for key, info in ALL_ANALYSTS.items():
            style = info["style"]
            if style not in styles:
                styles[style] = []
            styles[style].append((key, info))

        if 'custom_analysts' not in st.session_state:
            st.session_state.custom_analysts = []

        selected_analysts = []
        for style, analysts in styles.items():
            st.caption(f"**{style}**")
            cols = st.columns(2)
            for i, (key, info) in enumerate(analysts):
                with cols[i % 2]:
                    if st.checkbox(f"{info['icon']} {info['name']}", key=f"custom_{key}"):
                        selected_analysts.append(key)

        st.session_state.custom_analysts = selected_analysts
        analysts_to_use = selected_analysts
    else:
        analysts_to_use = STRATEGIES.get(selected_strategy, {}).get("analysts", [])

    st.markdown("---")

    # Run button
    can_run = len(tickers) > 0 and (len(analysts_to_use) > 0 or selected_strategy != "custom")

    if st.button("🚀 Run Analysis", type="primary", use_container_width=True, disabled=not can_run):
        if selected_strategy and selected_strategy != "custom":
            analysts_to_use = STRATEGIES[selected_strategy]["analysts"]

        with st.spinner("Analyzing stocks..."):
            result = run_analysis(tickers, analysts_to_use, portfolio_value)
            if result:
                st.session_state.analysis_result = {
                    "result": result,
                    "tickers": tickers,
                    "portfolio_value": portfolio_value,
                    "strategy": selected_strategy,
                }
                st.success("Done!")
                st.rerun()

    if not can_run:
        if not selected_strategy:
            st.caption("⚠️ Please select a strategy")
        elif len(tickers) == 0:
            st.caption("⚠️ Please enter tickers")
        elif selected_strategy == "custom" and len(analysts_to_use) == 0:
            st.caption("⚠️ Please select analysts")


# ============== MAIN CONTENT ==============

if st.session_state.analysis_result:
    # Show results
    result_data = st.session_state.analysis_result
    stocks_data, portfolio_data = parse_result(result_data["result"], result_data["tickers"])
    portfolio_value = result_data.get("portfolio_value", 100000)
    strategy_key = result_data.get("strategy")
    strategy = STRATEGIES.get(strategy_key, {})

    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">Analysis Report</h1>', unsafe_allow_html=True)
    with col2:
        st.metric("Portfolio", f"${portfolio_value:,.0f}")
    with col3:
        st.metric("Strategy", strategy.get("name", "Custom").replace("🛡️ ", "").replace("⚖️ ", "").replace("📈 ", "").replace("🚀 ", "").replace("🎯 ", ""))

    st.markdown("---")

    if portfolio_data:
        # Portfolio Recommendations
        st.markdown("### 📊 Recommendations")

        cols = st.columns(len(portfolio_data))
        for i, item in enumerate(portfolio_data):
            with cols[i]:
                action_color = "#22c55e" if item["action"] in ["BUY", "LONG"] else "#ef4444" if item["action"] == "SHORT" else "#6b7280"
                bg_start = "#064e3b" if item["action"] in ["BUY", "LONG"] else "#7f1d1d" if item["action"] == "SHORT" else "#1f2937"

                st.markdown(f"""
                <div style="background: linear-gradient(180deg, {bg_start} 0%, #111827 100%);
                            padding: 20px; border-radius: 16px; border: 1px solid #374151; height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <span style="font-size: 28px; font-weight: bold; color: white;">{item['ticker']}</span>
                        <span style="background: {action_color}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold;">
                            {item['action']}
                        </span>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <div style="color: #9ca3af; font-size: 11px; text-transform: uppercase;">Suggested Position</div>
                        <div style="color: white; font-size: 22px; font-weight: 600;">${item.get('position_value', 0):,.0f}</div>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <span style="color: #9ca3af; font-size: 11px;">Confidence</span>
                            <span style="color: white; font-size: 13px; font-weight: 600;">{item['confidence']:.0f}%</span>
                        </div>
                        <div style="background: #374151; border-radius: 6px; height: 8px;">
                            <div style="background: linear-gradient(90deg, #3b82f6, #8b5cf6); width: {item['confidence']}%; height: 100%; border-radius: 6px;"></div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <div style="flex: {max(item['bullish'], 0.5)}; background: #22c55e; padding: 6px 0; border-radius: 6px; text-align: center;">
                            <span style="color: white; font-size: 12px; font-weight: 600;">{item['bullish']} 📈</span>
                        </div>
                        <div style="flex: {max(item['neutral'], 0.5)}; background: #6b7280; padding: 6px 0; border-radius: 6px; text-align: center;">
                            <span style="color: white; font-size: 12px; font-weight: 600;">{item['neutral']} ➡️</span>
                        </div>
                        <div style="flex: {max(item['bearish'], 0.5)}; background: #ef4444; padding: 6px 0; border-radius: 6px; text-align: center;">
                            <span style="color: white; font-size: 12px; font-weight: 600;">{item['bearish']} 📉</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Summary row
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📈 Signal Distribution")
            total_bull = sum(p["bullish"] for p in portfolio_data)
            total_bear = sum(p["bearish"] for p in portfolio_data)
            total_neut = sum(p["neutral"] for p in portfolio_data)
            total = total_bull + total_bear + total_neut

            st.markdown(f"""
            <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                <div style="flex: 1; text-align: center; padding: 20px; background: linear-gradient(180deg, #064e3b 0%, #1f2937 100%); border-radius: 12px;">
                    <div style="font-size: 36px; font-weight: bold; color: #22c55e;">{total_bull}</div>
                    <div style="font-size: 13px; color: #9ca3af;">Bullish</div>
                </div>
                <div style="flex: 1; text-align: center; padding: 20px; background: linear-gradient(180deg, #374151 0%, #1f2937 100%); border-radius: 12px;">
                    <div style="font-size: 36px; font-weight: bold; color: #9ca3af;">{total_neut}</div>
                    <div style="font-size: 13px; color: #9ca3af;">Neutral</div>
                </div>
                <div style="flex: 1; text-align: center; padding: 20px; background: linear-gradient(180deg, #7f1d1d 0%, #1f2937 100%); border-radius: 12px;">
                    <div style="font-size: 36px; font-weight: bold; color: #ef4444;">{total_bear}</div>
                    <div style="font-size: 13px; color: #9ca3af;">Bearish</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if total > 0:
                st.markdown(f"""
                <div style="height: 24px; border-radius: 12px; overflow: hidden; display: flex; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
                    <div style="width: {(total_bull/total)*100}%; background: linear-gradient(90deg, #16a34a, #22c55e);"></div>
                    <div style="width: {(total_neut/total)*100}%; background: linear-gradient(90deg, #4b5563, #6b7280);"></div>
                    <div style="width: {(total_bear/total)*100}%; background: linear-gradient(90deg, #dc2626, #ef4444);"></div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 🏆 Analyst Confidence")
            if stocks_data:
                agent_stats = {}
                for stock in stocks_data:
                    for agent in stock["agents"]:
                        name = agent["agent"]
                        icon = agent.get("icon", "🤖")
                        if name not in agent_stats:
                            agent_stats[name] = {"total": 0, "confidence": 0, "icon": icon}
                        agent_stats[name]["total"] += 1
                        agent_stats[name]["confidence"] += agent["confidence"]

                sorted_agents = sorted(
                    [(name, stats["confidence"] / stats["total"], stats["icon"]) for name, stats in agent_stats.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

                for i, (name, avg_conf, icon) in enumerate(sorted_agents):
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else ""
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 12px 15px; background: #1f2937; border-radius: 10px; margin-bottom: 8px;">
                        <span style="font-size: 18px; margin-right: 10px;">{icon}</span>
                        <span style="flex: 1; color: white; font-size: 14px;">{name}</span>
                        <span style="color: #60a5fa; font-weight: bold; font-size: 16px;">{avg_conf:.0f}%</span>
                        <span style="margin-left: 8px;">{medal}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed Analysis
        st.markdown("### 📋 Detailed Analysis")

        for stock in stocks_data:
            with st.expander(f"**{stock['ticker']}** — {stock['bullish']} Bullish | {stock['neutral']} Neutral | {stock['bearish']} Bearish"):
                for agent in stock["agents"]:
                    signal_color = "#22c55e" if agent["signal"] == "BULLISH" else "#ef4444" if agent["signal"] == "BEARISH" else "#6b7280"
                    st.markdown(f"""
                    <div style="background: #1f2937; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid {signal_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span style="font-size: 18px; margin-right: 8px;">{agent.get('icon', '🤖')}</span>
                                <strong style="color: white; font-size: 15px;">{agent['agent']}</strong>
                            </div>
                            <span style="background: {signal_color}25; color: {signal_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{agent['signal']}</span>
                        </div>
                        <div style="color: #60a5fa; font-size: 13px; margin-bottom: 8px;">Confidence: {agent['confidence']:.0f}%</div>
                        <div style="color: #9ca3af; font-size: 13px; line-height: 1.6;">{agent['reasoning']}</div>
                    </div>
                    """, unsafe_allow_html=True)

else:
    # Welcome screen with instructions
    st.markdown('<h1 class="main-header">AI Hedge Fund Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Get AI-powered stock analysis from legendary investors</p>', unsafe_allow_html=True)

    st.markdown("---")

    # How it works
    st.markdown("### 🚀 How It Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="instruction-card">
            <div style="font-size: 40px; margin-bottom: 15px;">1️⃣</div>
            <h4 style="color: white; margin-bottom: 10px;">Choose Stocks</h4>
            <p style="color: #9ca3af; font-size: 14px;">Enter tickers like AAPL, MSFT, or use portfolio mode to get recommendations based on your investment amount.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="instruction-card">
            <div style="font-size: 40px; margin-bottom: 15px;">2️⃣</div>
            <h4 style="color: white; margin-bottom: 10px;">Select Strategy</h4>
            <p style="color: #9ca3af; font-size: 14px;">Pick a strategy matching your risk tolerance. Each strategy uses different AI analysts suited for that approach.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="instruction-card">
            <div style="font-size: 40px; margin-bottom: 15px;">3️⃣</div>
            <h4 style="color: white; margin-bottom: 10px;">Get Analysis</h4>
            <p style="color: #9ca3af; font-size: 14px;">Receive BUY/HOLD/SHORT recommendations with confidence scores and detailed reasoning from each analyst.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Strategy overview
    st.markdown("### 📊 Investment Strategies")

    cols = st.columns(4)
    strategies_display = ["conservative", "balanced", "growth", "aggressive"]

    for i, key in enumerate(strategies_display):
        strategy = STRATEGIES[key]
        with cols[i]:
            st.markdown(f"""
            <div style="background: #1f2937; padding: 20px; border-radius: 12px; border: 2px solid {strategy['color']}30; text-align: center; height: 200px;">
                <div style="font-size: 28px; margin-bottom: 10px;">{strategy['name'].split()[0]}</div>
                <div style="color: white; font-size: 16px; font-weight: 600; margin-bottom: 8px;">{strategy['name'].split()[1] if len(strategy['name'].split()) > 1 else ''}</div>
                <div style="color: {strategy['color']}; font-size: 13px; font-weight: 600; margin-bottom: 10px;">Risk: {strategy['risk']}</div>
                <div style="color: #9ca3af; font-size: 12px;">{strategy['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # AI Analysts preview
    st.markdown("### 🤖 AI Analysts")
    st.caption("Our team of AI analysts modeled after legendary investors")

    cols = st.columns(6)
    analysts_preview = list(ALL_ANALYSTS.items())[:6]

    for i, (key, info) in enumerate(analysts_preview):
        with cols[i]:
            st.markdown(f"""
            <div style="background: #1f2937; padding: 15px; border-radius: 10px; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 8px;">{info['icon']}</div>
                <div style="color: white; font-size: 13px; font-weight: 600;">{info['name']}</div>
                <div style="color: #6b7280; font-size: 11px;">{info['style']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Call to action
    st.markdown("""
    <div style="text-align: center; padding: 30px;">
        <p style="color: #9ca3af; font-size: 16px;">👈 Use the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Built with Streamlit | AI Hedge Fund Analysis Tool | Demo uses sample data")

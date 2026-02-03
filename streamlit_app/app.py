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
    .signal-bullish { color: #22c55e; font-weight: bold; }
    .signal-bearish { color: #ef4444; font-weight: bold; }
    .signal-neutral { color: #6b7280; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Available analysts
ANALYSTS = [
    {"key": "warren_buffett", "name": "Warren Buffett", "desc": "Value investing principles"},
    {"key": "charlie_munger", "name": "Charlie Munger", "desc": "Mental models approach"},
    {"key": "ben_graham", "name": "Ben Graham", "desc": "Security analysis fundamentals"},
    {"key": "peter_lynch", "name": "Peter Lynch", "desc": "Growth at reasonable price"},
    {"key": "phil_fisher", "name": "Phil Fisher", "desc": "Scuttlebutt method"},
    {"key": "stanley_druckenmiller", "name": "Stanley Druckenmiller", "desc": "Macro investing"},
    {"key": "bill_ackman", "name": "Bill Ackman", "desc": "Activist investing"},
    {"key": "cathie_wood", "name": "Cathie Wood", "desc": "Disruptive innovation"},
    {"key": "fundamentals_agent", "name": "Fundamentals Agent", "desc": "Financial metrics analysis"},
    {"key": "technical_agent", "name": "Technical Agent", "desc": "Chart patterns & indicators"},
    {"key": "sentiment_agent", "name": "Sentiment Agent", "desc": "News & social sentiment"},
    {"key": "valuation_agent", "name": "Valuation Agent", "desc": "DCF & relative valuation"},
]

# Sample results data (for demo when API is not available)
SAMPLE_RESULTS = {
    "AAPL": {
        "warren_buffett": {"signal": "BULLISH", "confidence": 75, "reasoning": "Strong brand moat, consistent cash flows, and excellent management make Apple a classic Buffett-style investment."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 70, "reasoning": "Apple's ecosystem creates powerful network effects and switching costs."},
        "ben_graham": {"signal": "NEUTRAL", "confidence": 55, "reasoning": "Current valuation is above intrinsic value based on traditional metrics."},
        "technical_agent": {"signal": "BULLISH", "confidence": 68, "reasoning": "Price above 50-day and 200-day moving averages, RSI showing strength."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 72, "reasoning": "Positive sentiment from recent product announcements and earnings."},
    },
    "MSFT": {
        "warren_buffett": {"signal": "BULLISH", "confidence": 80, "reasoning": "Cloud computing dominance and AI integration provide durable competitive advantages."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 78, "reasoning": "Microsoft's multiple revenue streams and enterprise relationships are exceptional."},
        "ben_graham": {"signal": "NEUTRAL", "confidence": 50, "reasoning": "Trading at premium to historical averages, margin of safety is limited."},
        "technical_agent": {"signal": "BULLISH", "confidence": 65, "reasoning": "Uptrend intact, support levels holding well."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 85, "reasoning": "AI narrative driving strong positive sentiment."},
    },
    "NVDA": {
        "warren_buffett": {"signal": "NEUTRAL", "confidence": 45, "reasoning": "Excellent business but valuation makes it speculative at current prices."},
        "charlie_munger": {"signal": "BULLISH", "confidence": 65, "reasoning": "NVIDIA has a temporary monopoly in AI chips which could last years."},
        "ben_graham": {"signal": "BEARISH", "confidence": 70, "reasoning": "P/E ratio far exceeds reasonable bounds for value investing."},
        "technical_agent": {"signal": "BULLISH", "confidence": 60, "reasoning": "Strong momentum but showing signs of exhaustion."},
        "sentiment_agent": {"signal": "BULLISH", "confidence": 90, "reasoning": "AI hype cycle driving extreme positive sentiment."},
    },
}


def run_analysis_demo(tickers: list, analysts: list):
    """Run demo analysis with sample data."""
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
            neutral = sum(1 for s in signals.values() if s["signal"] == "NEUTRAL")

            if bearish > bullish:
                action = "SHORT"
            elif bullish > bearish:
                action = "BUY"
            else:
                action = "HOLD"

            avg_conf = sum(s["confidence"] for s in signals.values()) / len(signals) if signals else 0

            result["decisions"]["decisions"].append({
                "ticker": ticker_upper,
                "action": action,
                "quantity": abs(bullish - bearish) * 20,
                "confidence": avg_conf,
            })

    return result


def run_analysis_live(tickers: list, analysts: list, model_name: str = "gpt-4o-mini"):
    """Run live analysis using OpenAI API."""
    try:
        # Check for API key
        api_key = None
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            pass

        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            st.warning("No OpenAI API key found. Using demo mode with sample data.")
            return run_analysis_demo(tickers, analysts)

        os.environ["OPENAI_API_KEY"] = api_key

        # Try to import and run the actual hedge fund
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

        from datetime import datetime, timedelta
        from src.main import run_hedge_fund

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        portfolio = {
            "cash": 100000,
            "margin_requirement": 0.0,
            "margin_used": 0.0,
            "positions": {t: {"long": 0, "short": 0, "long_cost_basis": 0.0, "short_cost_basis": 0.0, "short_margin_used": 0.0} for t in tickers},
            "realized_gains": {t: {"long": 0.0, "short": 0.0} for t in tickers},
        }

        result = run_hedge_fund(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            portfolio=portfolio,
            show_reasoning=True,
            selected_analysts=analysts,
            model_name=model_name,
            model_provider="OpenAI",
        )
        return result

    except ImportError as e:
        st.warning(f"Live analysis not available: {e}. Using demo mode.")
        return run_analysis_demo(tickers, analysts)
    except Exception as e:
        st.error(f"Analysis failed: {e}. Falling back to demo mode.")
        return run_analysis_demo(tickers, analysts)


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
            agents.append({
                "agent": agent_key.replace("_", " ").title(),
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
            "bullish": bull,
            "bearish": bear,
            "neutral": neut,
        })

    return stocks_data, portfolio_data


# Sidebar
with st.sidebar:
    st.title("📈 AI Hedge Fund")
    st.markdown("---")

    # Tickers input
    st.subheader("Stock Tickers")
    ticker_input = st.text_input(
        "Enter tickers (comma-separated)",
        value="AAPL, MSFT, NVDA",
        help="Enter stock ticker symbols separated by commas"
    )
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    st.markdown("---")

    # Analyst selection
    st.subheader("AI Analysts")
    st.caption("Select which AI agents to use")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Select All", use_container_width=True):
            st.session_state.selected_analysts = [a["key"] for a in ANALYSTS]
    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.selected_analysts = []

    if 'selected_analysts' not in st.session_state:
        st.session_state.selected_analysts = [a["key"] for a in ANALYSTS[:5]]

    selected = []
    for analyst in ANALYSTS:
        if st.checkbox(
            analyst["name"],
            value=analyst["key"] in st.session_state.selected_analysts,
            help=analyst["desc"],
            key=f"analyst_{analyst['key']}"
        ):
            selected.append(analyst["key"])
    st.session_state.selected_analysts = selected

    st.markdown("---")

    # Run button
    run_disabled = len(tickers) == 0 or len(selected) == 0
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True, disabled=run_disabled):
        with st.spinner("Running analysis..."):
            result = run_analysis_live(tickers, selected)
            if result:
                st.session_state.analysis_result = {
                    "result": result,
                    "tickers": tickers,
                }
                st.success("Analysis complete!")
                st.rerun()

    st.markdown("---")
    st.caption("💡 Demo mode uses sample data. Add OPENAI_API_KEY in secrets for live analysis.")

# Main content
st.title("AI Hedge Fund Analysis")

if st.session_state.analysis_result:
    result_data = st.session_state.analysis_result
    stocks_data, portfolio_data = parse_result(result_data["result"], result_data["tickers"])

    if portfolio_data:
        # Portfolio Recommendations
        st.header("📊 Portfolio Recommendations")

        cols = st.columns(len(portfolio_data))
        for i, item in enumerate(portfolio_data):
            with cols[i]:
                action_color = "#22c55e" if item["action"] in ["BUY", "LONG"] else "#ef4444" if item["action"] == "SHORT" else "#6b7280"
                bg_color = "#064e3b" if item["action"] in ["BUY", "LONG"] else "#7f1d1d" if item["action"] == "SHORT" else "#1f2937"
                border_color = "#065f46" if item["action"] in ["BUY", "LONG"] else "#991b1b" if item["action"] == "SHORT" else "#374151"

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {bg_color} 0%, #111827 100%);
                            padding: 20px; border-radius: 12px; border: 1px solid {border_color}; margin-bottom: 10px;">
                    <h2 style="margin: 0; color: white;">{item['ticker']}</h2>
                    <span style="background: {action_color}; color: white; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: bold;">
                        {item['action']}
                    </span>
                    <p style="margin: 15px 0 5px 0; color: #9ca3af; font-size: 12px;">Position</p>
                    <p style="margin: 0; color: white; font-size: 24px; font-weight: bold;">{item['quantity']} shares</p>
                    <p style="margin: 15px 0 5px 0; color: #9ca3af; font-size: 12px;">Confidence</p>
                    <div style="background: #374151; border-radius: 4px; height: 8px; margin-bottom: 5px;">
                        <div style="background: {'#22c55e' if item['confidence'] >= 70 else '#eab308' if item['confidence'] >= 40 else '#ef4444'};
                                    width: {item['confidence']}%; height: 100%; border-radius: 4px;"></div>
                    </div>
                    <p style="margin: 0; color: white; font-size: 14px;">{item['confidence']:.0f}%</p>
                    <div style="display: flex; gap: 4px; margin-top: 15px;">
                        <div style="flex: {max(item['bullish'], 0.1)}; background: #22c55e; padding: 4px; border-radius: 4px; text-align: center; color: white; font-size: 12px;">{item['bullish']}</div>
                        <div style="flex: {max(item['neutral'], 0.1)}; background: #6b7280; padding: 4px; border-radius: 4px; text-align: center; color: white; font-size: 12px;">{item['neutral']}</div>
                        <div style="flex: {max(item['bearish'], 0.1)}; background: #ef4444; padding: 4px; border-radius: 4px; text-align: center; color: white; font-size: 12px;">{item['bearish']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Signal Summary
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Signal Summary")
            total_bull = sum(p["bullish"] for p in portfolio_data)
            total_bear = sum(p["bearish"] for p in portfolio_data)
            total_neut = sum(p["neutral"] for p in portfolio_data)
            total = total_bull + total_bear + total_neut

            if total > 0:
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <div style="flex: 1; text-align: center; padding: 15px; background: #064e3b; border-radius: 8px;">
                        <div style="font-size: 28px; font-weight: bold; color: #22c55e;">{total_bull}</div>
                        <div style="font-size: 12px; color: #9ca3af;">Bullish</div>
                    </div>
                    <div style="flex: 1; text-align: center; padding: 15px; background: #1f2937; border-radius: 8px;">
                        <div style="font-size: 28px; font-weight: bold; color: #6b7280;">{total_neut}</div>
                        <div style="font-size: 12px; color: #9ca3af;">Neutral</div>
                    </div>
                    <div style="flex: 1; text-align: center; padding: 15px; background: #7f1d1d; border-radius: 8px;">
                        <div style="font-size: 28px; font-weight: bold; color: #ef4444;">{total_bear}</div>
                        <div style="font-size: 12px; color: #9ca3af;">Bearish</div>
                    </div>
                </div>
                <div style="height: 20px; border-radius: 10px; overflow: hidden; display: flex;">
                    <div style="width: {(total_bull/total)*100}%; background: #22c55e;"></div>
                    <div style="width: {(total_neut/total)*100}%; background: #6b7280;"></div>
                    <div style="width: {(total_bear/total)*100}%; background: #ef4444;"></div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("🏆 Top Agents by Confidence")
            if stocks_data:
                agent_stats = {}
                for stock in stocks_data:
                    for agent in stock["agents"]:
                        name = agent["agent"]
                        if name not in agent_stats:
                            agent_stats[name] = {"total": 0, "confidence": 0}
                        agent_stats[name]["total"] += 1
                        agent_stats[name]["confidence"] += agent["confidence"]

                sorted_agents = sorted(
                    [(name, stats["confidence"] / stats["total"]) for name, stats in agent_stats.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]

                for i, (name, avg_conf) in enumerate(sorted_agents):
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 10px; background: #1f2937; border-radius: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px; margin-right: 12px;">{medal}</span>
                        <span style="flex: 1; color: white; font-size: 14px;">{name}</span>
                        <span style="color: #60a5fa; font-weight: bold; font-size: 16px;">{avg_conf:.0f}%</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        # Detailed Analysis
        st.header("📋 Detailed Analysis")

        for stock in stocks_data:
            with st.expander(f"**{stock['ticker']}** — {stock['bullish']} Bullish | {stock['neutral']} Neutral | {stock['bearish']} Bearish"):
                for agent in stock["agents"]:
                    signal_color = "#22c55e" if agent["signal"] == "BULLISH" else "#ef4444" if agent["signal"] == "BEARISH" else "#6b7280"
                    st.markdown(f"""
                    <div style="background: #1f2937; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {signal_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong style="color: white; font-size: 16px;">{agent['agent']}</strong>
                            <span style="background: {signal_color}30; color: {signal_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{agent['signal']}</span>
                        </div>
                        <div style="color: #60a5fa; font-size: 13px; margin-bottom: 8px;">Confidence: {agent['confidence']:.0f}%</div>
                        <div style="color: #9ca3af; font-size: 13px; line-height: 1.5;">{agent['reasoning']}</div>
                    </div>
                    """, unsafe_allow_html=True)

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: white;">Welcome to AI Hedge Fund Analysis</h2>
        <p style="color: #9ca3af; font-size: 16px; margin-bottom: 30px;">
            Select your tickers and AI analysts from the sidebar, then click <strong>Run Analysis</strong> to get started.
        </p>

        <div style="max-width: 600px; margin: 0 auto; text-align: left;">
            <h4 style="color: white;">How it works:</h4>
            <ol style="color: #9ca3af; line-height: 2;">
                <li>Enter stock tickers (e.g., AAPL, MSFT, NVDA)</li>
                <li>Select AI analysts to evaluate the stocks</li>
                <li>Each analyst provides a signal (Bullish/Bearish/Neutral) with confidence</li>
                <li>The system aggregates signals into trading recommendations</li>
            </ol>
        </div>

        <div style="margin-top: 40px; padding: 20px; background: #1f2937; border-radius: 12px; max-width: 500px; margin-left: auto; margin-right: auto;">
            <p style="color: #9ca3af; margin: 0;">
                💡 <strong>Demo Mode:</strong> Try it now with sample data.<br>
                Add your <code>OPENAI_API_KEY</code> in secrets for live AI analysis.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6b7280; font-size: 12px;'>Built with Streamlit | AI Hedge Fund Analysis Tool</p>",
    unsafe_allow_html=True
)

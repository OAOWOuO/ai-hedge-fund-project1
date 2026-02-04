"""
AI Hedge Fund Terminal v4.3
P0 fixes: allocation caps, HTML rendering, duplicate keys, analyst state, fractional rounding
P1: allocation audit trail, consolidated lookup, improved charts, analysts tab
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
from typing import Dict, List

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="AI Hedge Fund Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============== CSS ==============
st.markdown("""
<style>
    .main { background: #0d1117; }
    .stApp { background: #0d1117; }
    #MainMenu, footer, header { visibility: hidden; }
    h1, h2, h3, h4 { color: #e6edf3 !important; font-weight: 600 !important; }
    p, span, label, li { color: #c9d1d9 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #161b22; padding: 8px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #8b949e; border-radius: 6px; padding: 8px 16px; }
    .stTabs [aria-selected="true"] { background: #238636 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ============== ALLOCATION MODES ==============
ALLOCATION_MODES = {
    "max_deploy": {"name": "Maximum Deployment", "desc": "Deploy 95%+ of capital. Position caps scale with # of tickers.", "target_pct": 0.95},
    "equal_weight": {"name": "Equal Weight", "desc": "Split capital equally among actionable tickers.", "target_pct": 0.90},
    "confidence_weighted": {"name": "Confidence Weighted", "desc": "Size by conviction. May hold cash.", "target_pct": None},
    "conservative": {"name": "Conservative", "desc": "High-conviction only. 30-50% cash buffer.", "target_pct": 0.50}
}

# ============== ANALYST DEFINITIONS ==============
ANALYST_CATEGORIES = {
    "Value Investors": {
        "warren_buffett": {"name": "Warren Buffett", "desc": "Moats, quality management, long-term value", "bias": -0.1,
            "thesis": "Seeks companies with durable competitive advantages (moats) trading below intrinsic value",
            "drivers": "Strong brand, pricing power, consistent earnings, quality management",
            "horizon": "5-10+ years", "risks": "May miss growth opportunities, slow to act"},
        "charlie_munger": {"name": "Charlie Munger", "desc": "Mental models, business quality", "bias": -0.1,
            "thesis": "Focus on business quality and management integrity over pure value metrics",
            "drivers": "Mental models, avoiding stupidity, quality over price",
            "horizon": "Long-term", "risks": "Concentration risk, patience required"},
        "ben_graham": {"name": "Benjamin Graham", "desc": "Margin of safety, net-net value", "bias": -0.15,
            "thesis": "Deep value requiring significant discount to book value",
            "drivers": "Net current asset value, margin of safety, quantitative screens",
            "horizon": "1-3 years", "risks": "Value traps, declining businesses"},
        "joel_greenblatt": {"name": "Joel Greenblatt", "desc": "Magic formula: ROIC + earnings yield", "bias": -0.05,
            "thesis": "Quantitative value screening based on return on capital and earnings yield",
            "drivers": "High ROIC, high earnings yield, systematic approach",
            "horizon": "1-2 years", "risks": "Sector concentration, mechanical approach"},
        "seth_klarman": {"name": "Seth Klarman", "desc": "Deep value, distressed assets", "bias": -0.15,
            "thesis": "Contrarian deep value in distressed or out-of-favor situations",
            "drivers": "Extreme pessimism, catalyst identification, risk management",
            "horizon": "2-5 years", "risks": "Timing uncertainty, permanent capital loss"},
    },
    "Growth Investors": {
        "peter_lynch": {"name": "Peter Lynch", "desc": "PEG ratio, growth at reasonable price", "bias": 0.05,
            "thesis": "Growth at a reasonable price, invest in what you understand",
            "drivers": "PEG ratio, local knowledge, growth sustainability",
            "horizon": "3-5 years", "risks": "Overpaying for growth, diversification"},
        "phil_fisher": {"name": "Philip Fisher", "desc": "Scuttlebutt, quality growth", "bias": 0.05,
            "thesis": "Long-term growth investing with deep qualitative research",
            "drivers": "Management quality, R&D, competitive position, scuttlebutt",
            "horizon": "10+ years", "risks": "Concentration, qualitative biases"},
        "cathie_wood": {"name": "Cathie Wood", "desc": "Disruptive innovation, exponential growth", "bias": 0.2,
            "thesis": "High-conviction bets on disruptive innovation and exponential growth",
            "drivers": "Disruption potential, TAM expansion, Wright's Law cost curves",
            "horizon": "5+ years", "risks": "Volatility, valuation, execution risk"},
        "bill_ackman": {"name": "Bill Ackman", "desc": "Activist catalysts, concentrated bets", "bias": 0.1,
            "thesis": "Concentrated positions with activist catalysts to unlock value",
            "drivers": "Undervalued assets, activist engagement, management change",
            "horizon": "2-4 years", "risks": "Concentration, activism resistance"},
    },
    "Macro Traders": {
        "stanley_druckenmiller": {"name": "Stanley Druckenmiller", "desc": "Macro trends, asymmetric bets", "bias": 0,
            "thesis": "Macro trend following with aggressive sizing on high-conviction ideas",
            "drivers": "Liquidity cycles, central bank policy, asymmetric setups",
            "horizon": "Months to years", "risks": "Timing, leverage"},
        "george_soros": {"name": "George Soros", "desc": "Reflexivity, regime changes", "bias": 0,
            "thesis": "Identifies reflexive feedback loops and regime changes",
            "drivers": "Market psychology, reflexivity, boom-bust cycles",
            "horizon": "Variable", "risks": "Timing, complexity"},
        "ray_dalio": {"name": "Ray Dalio", "desc": "Economic machine, risk parity", "bias": -0.05,
            "thesis": "Systematic macro based on economic machine principles",
            "drivers": "Debt cycles, productivity, diversification",
            "horizon": "Full cycle", "risks": "Model assumptions, correlation breakdown"},
        "paul_tudor_jones": {"name": "Paul Tudor Jones", "desc": "Technical macro, trend following", "bias": 0,
            "thesis": "Technical analysis combined with macro themes",
            "drivers": "Price action, trend, sentiment extremes",
            "horizon": "Weeks to months", "risks": "Whipsaws, false signals"},
    },
    "Quantitative Agents": {
        "fundamentals_agent": {"name": "Fundamentals Analyst", "desc": "Financial ratios, earnings quality", "bias": 0,
            "thesis": "Analyzes financial statements, ratios, and earnings quality",
            "drivers": "Revenue growth, margins, ROE, debt levels, cash flow",
            "horizon": "1-2 years", "risks": "Backward looking, accounting manipulation"},
        "technical_agent": {"name": "Technical Analyst", "desc": "Price patterns, momentum, RSI, MACD", "bias": 0,
            "thesis": "Technical indicators and price pattern analysis",
            "drivers": "RSI, MACD, moving averages, support/resistance",
            "horizon": "Days to weeks", "risks": "False signals, changing regimes"},
        "sentiment_agent": {"name": "Sentiment Analyst", "desc": "News sentiment, social media", "bias": 0.05,
            "thesis": "Aggregates news sentiment, social media buzz, analyst ratings",
            "drivers": "News flow, social sentiment, analyst revisions",
            "horizon": "Days to months", "risks": "Noise, manipulation, lag"},
        "valuation_agent": {"name": "Valuation Analyst", "desc": "DCF, comparable analysis", "bias": -0.05,
            "thesis": "DCF models, comparable company analysis, sum-of-parts",
            "drivers": "Intrinsic value, multiples, growth assumptions",
            "horizon": "1-3 years", "risks": "Model sensitivity, assumptions"},
        "momentum_agent": {"name": "Momentum Analyst", "desc": "Price and earnings momentum", "bias": 0.1,
            "thesis": "Follows price and earnings momentum trends",
            "drivers": "Price momentum, earnings surprises, estimate revisions",
            "horizon": "3-12 months", "risks": "Reversals, crowding"},
        "risk_agent": {"name": "Risk Analyst", "desc": "Volatility, drawdown, tail risk", "bias": -0.1,
            "thesis": "Focuses on risk metrics and downside protection",
            "drivers": "Volatility, drawdown, VaR, correlation, tail risk",
            "horizon": "Ongoing", "risks": "Over-conservatism, missed upside"},
    },
}


def get_all_analysts():
    result = {}
    for cat, analysts in ANALYST_CATEGORIES.items():
        for key, info in analysts.items():
            result[key] = {**info, "category": cat}
    return result

ALL_ANALYSTS = get_all_analysts()
ALL_ANALYST_KEYS = list(ALL_ANALYSTS.keys())


# ============== RISK PARAMETERS ==============
def get_risk_params(risk_level: float, custom: dict = None) -> dict:
    params = {
        "max_position_pct": {"value": round(10 + risk_level * 25, 1), "unit": "%", "desc": "Max allocation per position"},
        "stop_loss_pct": {"value": round(20 - risk_level * 15, 1), "unit": "%", "desc": "Stop loss distance"},
        "take_profit_pct": {"value": round(15 + risk_level * 45, 1), "unit": "%", "desc": "Take profit target"},
        "min_confidence": {"value": round(65 - risk_level * 35, 0), "unit": "%", "desc": "Min confidence to trade"},
        "leverage_cap": {"value": round(1.0 + risk_level * 1.0, 2), "unit": "x", "desc": "Max leverage"},
    }
    if custom:
        for k, v in custom.items():
            if k in params and v is not None:
                params[k]["value"] = v
    return params


# ============== STOCK DATA ==============
@st.cache_data(ttl=300)
def fetch_stock(ticker: str) -> dict:
    ts = datetime.now()
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        info = stock.info
        if len(hist) >= 1:
            price = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price
            return {
                "valid": True, "ticker": ticker, "price": price,
                "change": price - prev, "change_pct": ((price - prev) / prev * 100) if prev else 0,
                "name": info.get("shortName", ticker), "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap", 0), "pe_ratio": info.get("trailingPE") or 0,
                "beta": info.get("beta") or 1.0, "high_52w": info.get("fiftyTwoWeekHigh") or 0,
                "low_52w": info.get("fiftyTwoWeekLow") or 0, "timestamp": ts
            }
    except:
        pass
    return {"valid": False, "ticker": ticker, "price": 0, "change": 0, "change_pct": 0,
            "name": ticker, "sector": "Unknown", "timestamp": ts}


@st.cache_data(ttl=300)
def fetch_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        import yfinance as yf
        return yf.Ticker(ticker).history(period=period)
    except:
        return pd.DataFrame()


# ============== ANALYSIS ENGINE ==============
def run_analysis(tickers: List[str], analysts: List[str], risk_level: float, capital: float,
                 holdings: Dict[str, int], mode_key: str, allow_fractional: bool = False,
                 custom_params: dict = None) -> dict:
    """Run analysis with proper dynamic position caps and full audit trail."""

    sorted_analysts = sorted(analysts)
    seed_str = f"{sorted(tickers)}{sorted_analysts}{risk_level:.2f}{capital}{mode_key}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)

    risk_params = get_risk_params(risk_level, custom_params)
    mode = ALLOCATION_MODES[mode_key]
    timestamp = datetime.now()

    # ===== AUDIT TRAIL =====
    audit = {
        "inputs": {"tickers": tickers, "analysts": sorted_analysts, "capital": capital,
                   "mode": mode["name"], "risk_level": f"{risk_level:.0%}"},
        "steps": []
    }

    # ===== PHASE 1: SIGNALS =====
    ticker_results = {}

    for ticker in tickers:
        np.random.seed(seed)
        stock = fetch_stock(ticker)
        signals = []

        for analyst_key in sorted_analysts:
            if analyst_key not in ALL_ANALYSTS:
                continue
            info = ALL_ANALYSTS[analyst_key]
            sig_seed = int(hashlib.md5(f"{analyst_key}{ticker}{seed}".encode()).hexdigest()[:8], 16)
            np.random.seed(sig_seed)

            score = np.random.uniform(-1, 1) + info.get("bias", 0)
            if score > 0.2:
                signal, confidence = "BULLISH", 50 + score * 40
            elif score < -0.2:
                signal, confidence = "BEARISH", 50 + abs(score) * 40
            else:
                signal, confidence = "NEUTRAL", 40 + np.random.uniform(0, 20)

            signals.append({
                "analyst": info["name"], "analyst_key": analyst_key, "category": info["category"],
                "signal": signal, "confidence": min(95, max(30, confidence)), "score": score,
                "thesis": info.get("thesis", ""), "drivers": info.get("drivers", ""),
                "horizon": info.get("horizon", ""), "risks": info.get("risks", "")
            })

        bullish = sum(1 for s in signals if s["signal"] == "BULLISH")
        bearish = sum(1 for s in signals if s["signal"] == "BEARISH")
        neutral = len(signals) - bullish - bearish
        total = len(signals)
        avg_conf = np.mean([s["confidence"] for s in signals]) if signals else 50
        min_conf = risk_params["min_confidence"]["value"]

        if total == 0:
            action, reason = "HOLD", "No analysts selected"
        elif bullish > bearish and bullish >= neutral and avg_conf >= min_conf:
            action = "BUY"
            reason = f"Bullish consensus ({bullish}/{total}) at {avg_conf:.0f}% >= {min_conf:.0f}% threshold"
        elif bearish > bullish and bearish >= neutral and avg_conf >= min_conf:
            action = "SHORT"
            reason = f"Bearish consensus ({bearish}/{total}) at {avg_conf:.0f}% >= {min_conf:.0f}% threshold"
        elif avg_conf < min_conf:
            action, reason = "HOLD", f"Confidence {avg_conf:.0f}% below {min_conf:.0f}% threshold"
        else:
            action, reason = "HOLD", f"No consensus ({bullish}B/{neutral}N/{bearish}Be)"

        ticker_results[ticker] = {
            "stock": stock, "signals": signals, "bullish": bullish, "bearish": bearish,
            "neutral": neutral, "total": total, "avg_confidence": avg_conf,
            "action": action, "reason": reason, "holdings": holdings.get(ticker, 0)
        }

    # Audit: signals summary
    for t, r in ticker_results.items():
        audit["steps"].append(f"Signal: {t} → {r['action']} ({r['bullish']}B/{r['neutral']}N/{r['bearish']}Be, {r['avg_confidence']:.0f}% conf)")

    # ===== PHASE 2: ALLOCATION WITH DYNAMIC CAPS =====
    actionable = {t: r for t, r in ticker_results.items() if r["action"] != "HOLD" and r["stock"]["valid"]}
    n_actionable = len(actionable)

    positions = {}
    hold_tickers = {}
    cap_blocked = 0
    rounding_remainder = 0

    if n_actionable == 0:
        audit["steps"].append("No actionable tickers - 100% cash")
        for t, r in ticker_results.items():
            hold_tickers[t] = r["reason"]
    else:
        # DYNAMIC POSITION CAP: Scale based on number of actionable tickers
        base_cap = risk_params["max_position_pct"]["value"] / 100
        target_pct = mode.get("target_pct") or 0.5

        # Key fix: For max_deploy mode, allow position cap to scale up when few tickers
        if mode_key == "max_deploy":
            # Allow up to 95% per position if only 1 ticker, 47.5% if 2, etc.
            effective_cap = min(target_pct / n_actionable, 0.95)
            if effective_cap > base_cap:
                audit["steps"].append(f"Position cap scaled: {base_cap:.1%} → {effective_cap:.1%} (for {n_actionable} ticker(s) to reach {target_pct:.0%} target)")
        else:
            effective_cap = base_cap
            if n_actionable <= 2 and base_cap * n_actionable < target_pct:
                audit["steps"].append(f"Position cap {base_cap:.1%} × {n_actionable} tickers = {base_cap * n_actionable:.1%} max deployment")

        target_total = capital * target_pct
        audit["steps"].append(f"Target: deploy {target_pct:.0%} of ${capital:,.0f} = ${target_total:,.0f}")

        # Calculate per-position budget
        if mode_key == "confidence_weighted":
            total_conf = sum(r["avg_confidence"] for r in actionable.values())
        else:
            per_pos_budget = target_total / n_actionable
            audit["steps"].append(f"Per-position budget: ${per_pos_budget:,.0f}")

        for ticker, result in actionable.items():
            stock = result["stock"]
            price = stock["price"]

            if mode_key == "confidence_weighted":
                weight = result["avg_confidence"] / total_conf if total_conf > 0 else 1/n_actionable
                budget = capital * effective_cap * weight * (result["avg_confidence"] / 100)
            else:
                budget = per_pos_budget

            # Apply position cap
            max_budget = capital * effective_cap
            capped = budget > max_budget
            if capped:
                blocked = budget - max_budget
                cap_blocked += blocked
                budget = max_budget
                audit["steps"].append(f"{ticker}: capped at ${max_budget:,.0f} (${blocked:,.0f} blocked)")

            # Calculate shares
            if allow_fractional:
                shares = round(budget / price, 2)  # P0 fix: round to 2 decimals
                actual = shares * price
                remainder = budget - actual
            else:
                shares = int(budget / price)
                actual = shares * price
                remainder = budget - actual

            rounding_remainder += remainder

            # Stop loss / take profit
            sl_pct = risk_params["stop_loss_pct"]["value"]
            tp_pct = risk_params["take_profit_pct"]["value"]

            if result["action"] == "BUY":
                sl_price = price * (1 - sl_pct / 100)
                tp_price = price * (1 + tp_pct / 100)
                sl_dir, tp_dir = "below", "above"
            else:
                sl_price = price * (1 + sl_pct / 100)
                tp_price = price * (1 - tp_pct / 100)
                sl_dir, tp_dir = "above", "below"

            current = result["holdings"]
            delta = shares - current if result["action"] == "BUY" else -shares - current

            positions[ticker] = {
                "action": result["action"], "shares": shares, "price": price,
                "notional": actual, "pct": (actual / capital * 100) if capital else 0,
                "capped": capped, "sl_price": sl_price, "sl_pct": sl_pct, "sl_dir": sl_dir,
                "tp_price": tp_price, "tp_pct": tp_pct, "tp_dir": tp_dir,
                "current": current, "delta": delta, "confidence": result["avg_confidence"]
            }

            shares_fmt = f"{shares:.2f}" if allow_fractional else f"{shares:,}"
            audit["steps"].append(f"{ticker}: {result['action']} {shares_fmt} shares @ ${price:.2f} = ${actual:,.0f} ({actual/capital*100:.1f}%)")

        for t, r in ticker_results.items():
            if t not in positions:
                hold_tickers[t] = r["reason"]

    # ===== PHASE 3: SUMMARY =====
    long_exp = sum(p["notional"] for p in positions.values() if p["action"] == "BUY")
    short_exp = sum(p["notional"] for p in positions.values() if p["action"] == "SHORT")
    gross = long_exp + short_exp
    cash = capital - gross

    audit["steps"].append(f"Result: ${gross:,.0f} deployed ({gross/capital*100:.1f}%), ${cash:,.0f} cash ({cash/capital*100:.1f}%)")
    if cap_blocked > 0:
        audit["steps"].append(f"Cap blocked: ${cap_blocked:,.0f}")
    if rounding_remainder > 1:
        audit["steps"].append(f"Rounding remainder: ${rounding_remainder:,.0f}")

    return {
        "timestamp": timestamp,
        "config": {"tickers": tickers, "analysts": sorted_analysts, "analyst_count": len(sorted_analysts),
                   "capital": capital, "mode": mode["name"], "risk_level": risk_level},
        "risk_params": risk_params,
        "ticker_results": ticker_results,
        "positions": positions,
        "hold_tickers": hold_tickers,
        "audit": audit,
        "summary": {
            "capital": capital, "deployed": gross, "deployed_pct": (gross/capital*100) if capital else 0,
            "cash": cash, "cash_pct": (cash/capital*100) if capital else 0,
            "long": long_exp, "short": short_exp, "gross": gross, "net": long_exp - short_exp,
            "cap_blocked": cap_blocked, "rounding": rounding_remainder,
            "positions_count": len(positions), "hold_count": len(hold_tickers)
        }
    }


# ============== SESSION STATE - STABLE INITIALIZATION ==============
if "result" not in st.session_state:
    st.session_state.result = None
if "selected_analysts" not in st.session_state:
    st.session_state.selected_analysts = set(ALL_ANALYST_KEYS)  # Default all selected
if "custom_params" not in st.session_state:
    st.session_state.custom_params = {}
if "use_custom" not in st.session_state:
    st.session_state.use_custom = False
if "chart_period" not in st.session_state:
    st.session_state.chart_period = "1y"


# ============== HEADER ==============
st.markdown("# 📊 AI Hedge Fund Terminal")
st.caption("v4.3 | Yahoo Finance (15-20 min delayed)")

# ============== TABS ==============
tab_signals, tab_portfolio, tab_trades, tab_analysts, tab_securities, tab_settings = st.tabs([
    "📈 Signals", "💼 Portfolio", "📋 Trades", "🧠 Analysts", "🔍 Securities", "⚙️ Settings"
])


# ============== SIGNALS TAB ==============
with tab_signals:
    col_config, col_results = st.columns([1, 2])

    with col_config:
        st.subheader("Configuration")

        # Tickers
        ticker_input = st.text_input("Stock Tickers", value="AAPL, MSFT, NVDA, GOOGL",
                                      help="Comma-separated symbols")
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
        st.caption(f"{len(tickers)} ticker(s)")

        # Capital
        capital = st.number_input("Investment Capital ($)", min_value=1000, value=100000, step=10000)

        # Holdings
        with st.expander("Current Holdings"):
            holdings_text = st.text_area("TICKER:SHARES per line", placeholder="AAPL:50\nMSFT:30", height=80)
            holdings = {}
            for line in holdings_text.strip().split("\n"):
                if ":" in line:
                    try:
                        t, s = line.split(":")
                        holdings[t.strip().upper()] = int(s.strip())
                    except:
                        pass

        st.divider()

        # Mode
        mode_key = st.selectbox("Allocation Mode", options=list(ALLOCATION_MODES.keys()),
                                 format_func=lambda x: ALLOCATION_MODES[x]["name"])
        st.caption(ALLOCATION_MODES[mode_key]["desc"])

        allow_fractional = st.checkbox("Allow fractional shares", help="Paper trading only")

        st.divider()

        # Risk
        risk_level = st.slider("Risk Level", 0.0, 1.0, 0.5, 0.05)
        risk_label = "Conservative" if risk_level < 0.35 else "Aggressive" if risk_level > 0.65 else "Moderate"
        st.caption(f"{risk_label} ({risk_level:.0%})")

        st.divider()

        # Analysts - FIXED: No form, direct session state manipulation
        st.markdown("**AI Analysts**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Select All", key="btn_select_all", use_container_width=True):
                st.session_state.selected_analysts = set(ALL_ANALYST_KEYS)
                st.rerun()
        with col2:
            if st.button("Clear All", key="btn_clear_all", use_container_width=True):
                st.session_state.selected_analysts = set()
                st.rerun()

        # Display analyst checkboxes by category
        for cat, analysts in ANALYST_CATEGORIES.items():
            cat_count = sum(1 for k in analysts if k in st.session_state.selected_analysts)
            with st.expander(f"{cat} ({cat_count}/{len(analysts)})"):
                for key, info in analysts.items():
                    # Use stable key based on analyst key
                    is_selected = key in st.session_state.selected_analysts
                    if st.checkbox(info["name"], value=is_selected, key=f"chk_{key}", help=info["desc"]):
                        st.session_state.selected_analysts.add(key)
                    else:
                        st.session_state.selected_analysts.discard(key)

        selected_count = len(st.session_state.selected_analysts)
        st.markdown(f"**{selected_count}/{len(ALL_ANALYST_KEYS)}** analysts selected")

        st.divider()

        # Run button
        can_run = len(tickers) > 0 and selected_count > 0

        if st.button("🚀 RUN ANALYSIS", type="primary", use_container_width=True, disabled=not can_run):
            custom = st.session_state.custom_params if st.session_state.use_custom else None
            # Use current selected analysts
            analysts_to_use = list(st.session_state.selected_analysts)
            st.session_state.result = run_analysis(
                tickers=tickers,
                analysts=analysts_to_use,
                risk_level=risk_level,
                capital=capital,
                holdings=holdings,
                mode_key=mode_key,
                allow_fractional=allow_fractional,
                custom_params=custom
            )
            st.rerun()

        if not can_run:
            if len(tickers) == 0:
                st.warning("Enter at least one ticker")
            if selected_count == 0:
                st.warning("Select at least one analyst")

    # ===== RESULTS =====
    with col_results:
        if st.session_state.result:
            r = st.session_state.result
            s = r["summary"]

            st.subheader("Results")
            st.caption(f"Mode: {r['config']['mode']} | {r['config']['analyst_count']} analysts | {r['timestamp'].strftime('%H:%M:%S')}")

            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Capital", f"${s['capital']:,.0f}")
            c2.metric("Deployed", f"${s['deployed']:,.0f}", f"{s['deployed_pct']:.1f}%")
            c3.metric("Cash", f"${s['cash']:,.0f}", f"{s['cash_pct']:.1f}%")
            c4.metric("Max Loss", f"${sum(p['notional'] * p['sl_pct']/100 for p in r['positions'].values()):,.0f}")

            st.divider()

            # ===== ALLOCATION AUDIT TRAIL =====
            st.markdown("### Allocation Audit Trail")
            st.caption("Step-by-step breakdown showing exactly how capital was allocated")

            # Inputs
            audit = r["audit"]
            st.markdown(f"""
            **Inputs:** {len(audit['inputs']['tickers'])} tickers, {len(audit['inputs']['analysts'])} analysts,
            ${audit['inputs']['capital']:,.0f} capital, {audit['inputs']['mode']}, {audit['inputs']['risk_level']} risk
            """)

            # Steps
            for step in audit["steps"]:
                if "Signal:" in step:
                    st.markdown(f"🎯 {step}")
                elif "capped" in step.lower() or "blocked" in step.lower():
                    st.markdown(f"⚠️ {step}")
                elif "Result:" in step:
                    st.success(step)
                elif "cap scaled" in step.lower():
                    st.info(step)
                else:
                    st.markdown(f"→ {step}")

            st.divider()

            # Exposure
            st.markdown("### Exposure")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Long", f"${s['long']:,.0f}")
            c2.metric("Short", f"${s['short']:,.0f}")
            c3.metric("Gross", f"${s['gross']:,.0f}")
            c4.metric("Net", f"${s['net']:,.0f}")

            if s['short'] > 0:
                st.info(f"Short margin required: ${s['short'] * 0.5:,.0f} (50% Reg T)")

            st.divider()

            # Recommendations
            st.markdown("### Recommendations")

            for ticker, tr in r["ticker_results"].items():
                stock = tr["stock"]
                pos = r["positions"].get(ticker)

                col1, col2 = st.columns([4, 1])
                with col1:
                    if stock["valid"]:
                        chg = "▲" if stock["change"] >= 0 else "▼"
                        st.markdown(f"**{ticker}** — ${stock['price']:.2f} {chg}{abs(stock['change_pct']):.2f}%")
                        st.caption(f"{stock['name']} | {stock['sector']}")
                    else:
                        st.markdown(f"**{ticker}** — Price unavailable")
                with col2:
                    if tr["action"] == "BUY":
                        st.success(f"📈 BUY")
                    elif tr["action"] == "SHORT":
                        st.error(f"📉 SHORT")
                    else:
                        st.warning(f"⏸️ HOLD")

                st.caption(f"**Reason:** {tr['reason']}")

                if pos:
                    c1, c2, c3, c4 = st.columns(4)
                    shares_fmt = f"{pos['shares']:.2f}" if isinstance(pos['shares'], float) and pos['shares'] != int(pos['shares']) else f"{int(pos['shares']):,}"
                    c1.metric("Shares", shares_fmt)
                    c2.metric("Notional", f"${pos['notional']:,.0f}")
                    c3.metric("Stop Loss", f"${pos['sl_price']:.2f}")
                    c4.metric("Take Profit", f"${pos['tp_price']:.2f}")

                with st.expander(f"View {tr['total']} analyst signals"):
                    # Use proper dataframe instead of HTML
                    sig_data = []
                    for sig in tr["signals"]:
                        sig_data.append({
                            "Analyst": sig["analyst"],
                            "Category": sig["category"],
                            "Signal": sig["signal"],
                            "Confidence": f"{sig['confidence']:.0f}%"
                        })
                    if sig_data:
                        st.dataframe(pd.DataFrame(sig_data), hide_index=True, use_container_width=True)

                st.divider()

            # Export
            st.markdown("### Export")

            # Generate CSV
            if r["positions"]:
                csv_rows = ["Ticker,Action,Shares,Entry,Notional,Stop Loss,Take Profit,Confidence"]
                for t, p in r["positions"].items():
                    shares_str = f"{p['shares']:.2f}" if isinstance(p['shares'], float) else str(p['shares'])
                    csv_rows.append(f"{t},{p['action']},{shares_str},{p['price']:.2f},{p['notional']:.0f},{p['sl_price']:.2f},{p['tp_price']:.2f},{p['confidence']:.0f}")
                csv_data = "\n".join(csv_rows)
            else:
                csv_data = "No trades"

            # Generate text
            text_lines = [
                f"AI HEDGE FUND - TRADE LIST",
                f"Generated: {r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                f"Capital: ${r['config']['capital']:,.0f} | Mode: {r['config']['mode']}",
                f"Risk: {r['config']['risk_level']:.0%} | Analysts: {r['config']['analyst_count']}",
                "", "=" * 50, ""
            ]
            for t, p in r["positions"].items():
                shares_str = f"{p['shares']:.2f}" if isinstance(p['shares'], float) else str(p['shares'])
                text_lines.extend([
                    f"{p['action']} {shares_str} {t} @ ${p['price']:.2f}",
                    f"  Notional: ${p['notional']:,.0f} ({p['pct']:.1f}%)",
                    f"  Stop: ${p['sl_price']:.2f} ({p['sl_dir']}) | Target: ${p['tp_price']:.2f} ({p['tp_dir']})",
                    ""
                ])
            text_lines.extend([
                "=" * 50,
                f"Deployed: ${s['deployed']:,.0f} ({s['deployed_pct']:.1f}%)",
                f"Cash: ${s['cash']:,.0f} ({s['cash_pct']:.1f}%)",
                "", "DISCLAIMER: Educational use only. Not financial advice."
            ])
            text_data = "\n".join(text_lines)

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 CSV", csv_data, f"trades_{r['timestamp'].strftime('%Y%m%d_%H%M%S')}.csv",
                                   "text/csv", key="dl_csv_signals", use_container_width=True)
            with col2:
                st.download_button("📋 Text", text_data, f"trades_{r['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt",
                                   "text/plain", key="dl_txt_signals", use_container_width=True)

            with st.expander("Copy-Paste Format"):
                st.code(text_data, language=None)

        else:
            st.markdown("""
            ### Getting Started

            1. Enter ticker symbols (comma-separated)
            2. Set investment capital
            3. Choose allocation mode
            4. Adjust risk level
            5. Select AI analysts
            6. Click **RUN ANALYSIS**

            **Allocation Modes:**
            - **Maximum Deployment**: Deploys 95%+ capital. Position caps scale dynamically.
            - **Equal Weight**: Splits evenly among actionable tickers.
            - **Confidence Weighted**: Sizes by conviction.
            - **Conservative**: Large cash buffer.
            """)


# ============== PORTFOLIO TAB ==============
with tab_portfolio:
    st.subheader("Portfolio Overview")

    if st.session_state.result:
        r = st.session_state.result
        s = r["summary"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Positions", s["positions_count"])
        c2.metric("HOLD", s["hold_count"])
        c3.metric("Deployed", f"{s['deployed_pct']:.1f}%")
        c4.metric("Cash", f"{s['cash_pct']:.1f}%")

        st.divider()

        if r["positions"]:
            st.markdown("### Positions")
            pos_data = []
            for t, p in r["positions"].items():
                shares_fmt = f"{p['shares']:.2f}" if isinstance(p['shares'], float) and p['shares'] != int(p['shares']) else int(p['shares'])
                pos_data.append({
                    "Ticker": t, "Action": p["action"], "Shares": shares_fmt,
                    "Entry": f"${p['price']:.2f}", "Notional": f"${p['notional']:,.0f}",
                    "% Port": f"{p['pct']:.1f}%", "Stop Loss": f"${p['sl_price']:.2f}",
                    "Take Profit": f"${p['tp_price']:.2f}", "Conf": f"{p['confidence']:.0f}%"
                })
            st.dataframe(pd.DataFrame(pos_data), hide_index=True, use_container_width=True)

        if r["hold_tickers"]:
            st.markdown("### Not Trading (HOLD)")
            for t, reason in r["hold_tickers"].items():
                st.markdown(f"- **{t}**: {reason}")

        st.divider()

        st.markdown("### Cash Analysis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Undeployed", f"${s['cash']:,.0f}")
        c2.metric("Rounding", f"${s['rounding']:,.0f}")
        c3.metric("Cap Blocked", f"${s['cap_blocked']:,.0f}")

        # Export
        st.divider()
        if r["positions"]:
            csv_rows = ["Ticker,Action,Shares,Entry,Notional,Stop Loss,Take Profit,Confidence"]
            for t, p in r["positions"].items():
                shares_str = f"{p['shares']:.2f}" if isinstance(p['shares'], float) else str(p['shares'])
                csv_rows.append(f"{t},{p['action']},{shares_str},{p['price']:.2f},{p['notional']:.0f},{p['sl_price']:.2f},{p['tp_price']:.2f},{p['confidence']:.0f}")
            st.download_button("📥 Download CSV", "\n".join(csv_rows), "portfolio.csv", "text/csv",
                               key="dl_csv_portfolio", use_container_width=True)
    else:
        st.info("Run analysis from Signals tab first.")


# ============== TRADES TAB ==============
with tab_trades:
    st.subheader("Trade Instructions")

    if st.session_state.result:
        r = st.session_state.result

        if r["positions"]:
            trade_data = []
            for t, p in r["positions"].items():
                shares_fmt = f"{p['shares']:.2f}" if isinstance(p['shares'], float) and p['shares'] != int(p['shares']) else int(p['shares'])
                delta = p["delta"]
                delta_str = "New" if p["current"] == 0 else f"{delta:+,}" if isinstance(delta, int) else f"{delta:+.2f}"
                trade_data.append({
                    "Ticker": t, "Action": p["action"], "Shares": shares_fmt,
                    "Entry": f"${p['price']:.2f}", "Notional": f"${p['notional']:,.0f}",
                    "Stop": f"${p['sl_price']:.2f}", "Target": f"${p['tp_price']:.2f}",
                    "Delta": delta_str
                })
            st.dataframe(pd.DataFrame(trade_data), hide_index=True, use_container_width=True)

            st.divider()

            with st.expander("📝 Execution Notes", expanded=True):
                st.markdown("""
                - **Data delay**: Prices are 15-20 min delayed. Use live quotes.
                - **Order type**: Consider limit orders near entry prices.
                - **Stop losses**: Set immediately after entry. Direction matters for shorts.
                - **Margin**: Shorts require 50% initial margin (Reg T).
                """)

            st.divider()

            # Export
            csv_rows = ["Ticker,Action,Shares,Entry,Notional,Stop,Target,Delta"]
            for t, p in r["positions"].items():
                shares_str = f"{p['shares']:.2f}" if isinstance(p['shares'], float) else str(p['shares'])
                delta_str = "New" if p["current"] == 0 else str(p["delta"])
                csv_rows.append(f"{t},{p['action']},{shares_str},{p['price']:.2f},{p['notional']:.0f},{p['sl_price']:.2f},{p['tp_price']:.2f},{delta_str}")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 CSV", "\n".join(csv_rows), "trades.csv", "text/csv",
                                   key="dl_csv_trades", use_container_width=True)
            with col2:
                text_lines = [f"{p['action']} {p['shares']} {t} @ ${p['price']:.2f}" for t, p in r["positions"].items()]
                st.download_button("📋 Text", "\n".join(text_lines), "trades.txt", "text/plain",
                                   key="dl_txt_trades", use_container_width=True)
        else:
            st.info("No trades. All positions are HOLD.")
    else:
        st.info("Run analysis first.")


# ============== ANALYSTS TAB ==============
with tab_analysts:
    st.subheader("AI Analysts")

    if st.session_state.result:
        r = st.session_state.result
        selected = r["config"]["analysts"]

        st.markdown(f"### Selected Analysts ({len(selected)})")
        st.caption("Analysts that contributed to the current analysis")

        for analyst_key in selected:
            if analyst_key not in ALL_ANALYSTS:
                continue
            info = ALL_ANALYSTS[analyst_key]

            with st.expander(f"**{info['name']}** ({info['category']})"):
                st.markdown(f"**Thesis:** {info.get('thesis', 'N/A')}")
                st.markdown(f"**Key Drivers:** {info.get('drivers', 'N/A')}")
                st.markdown(f"**Time Horizon:** {info.get('horizon', 'N/A')}")
                st.markdown(f"**Risks:** {info.get('risks', 'N/A')}")
                st.markdown(f"**Bias:** {info.get('bias', 0):+.2f} (negative=bearish, positive=bullish)")

                # Show this analyst's signals for each ticker
                st.markdown("**Signals in this run:**")
                sig_data = []
                for ticker, tr in r["ticker_results"].items():
                    for sig in tr["signals"]:
                        if sig["analyst_key"] == analyst_key:
                            sig_data.append({
                                "Ticker": ticker,
                                "Signal": sig["signal"],
                                "Confidence": f"{sig['confidence']:.0f}%",
                                "Score": f"{sig['score']:.2f}"
                            })
                if sig_data:
                    st.dataframe(pd.DataFrame(sig_data), hide_index=True, use_container_width=True)

        st.divider()

        # Consensus breakdown per ticker
        st.markdown("### Consensus Breakdown")
        st.caption("How analyst signals rolled up to final decisions")

        for ticker, tr in r["ticker_results"].items():
            with st.expander(f"**{ticker}** → {tr['action']}"):
                st.markdown(f"**Final Decision:** {tr['action']}")
                st.markdown(f"**Reason:** {tr['reason']}")
                st.markdown(f"**Vote:** {tr['bullish']}B / {tr['neutral']}N / {tr['bearish']}Be")
                st.markdown(f"**Avg Confidence:** {tr['avg_confidence']:.0f}%")

                # Show rationale from top contributors
                bullish_sigs = [s for s in tr["signals"] if s["signal"] == "BULLISH"]
                bearish_sigs = [s for s in tr["signals"] if s["signal"] == "BEARISH"]

                if bullish_sigs:
                    st.markdown("**Bullish Arguments:**")
                    for s in sorted(bullish_sigs, key=lambda x: -x["confidence"])[:3]:
                        st.markdown(f"- {s['analyst']} ({s['confidence']:.0f}%): {s['thesis']}")

                if bearish_sigs:
                    st.markdown("**Bearish Arguments:**")
                    for s in sorted(bearish_sigs, key=lambda x: -x["confidence"])[:3]:
                        st.markdown(f"- {s['analyst']} ({s['confidence']:.0f}%): {s['thesis']}")

    else:
        st.markdown("### All Available Analysts")
        st.caption("Run an analysis to see specific signals")

        for cat, analysts in ANALYST_CATEGORIES.items():
            st.markdown(f"#### {cat}")
            for key, info in analysts.items():
                selected = "✅" if key in st.session_state.selected_analysts else "⬜"
                with st.expander(f"{selected} {info['name']}"):
                    st.markdown(f"**Thesis:** {info.get('thesis', 'N/A')}")
                    st.markdown(f"**Drivers:** {info.get('drivers', 'N/A')}")
                    st.markdown(f"**Horizon:** {info.get('horizon', 'N/A')}")
                    st.markdown(f"**Risks:** {info.get('risks', 'N/A')}")


# ============== SECURITIES TAB (CONSOLIDATED LOOKUP) ==============
with tab_securities:
    st.subheader("Securities Lookup")

    ticker = st.text_input("Enter ticker symbol", value="AAPL", placeholder="AAPL", key="securities_ticker")

    if ticker:
        ticker = ticker.upper()

        with st.spinner(f"Fetching {ticker}..."):
            stock = fetch_stock(ticker)

        if stock["valid"]:
            st.caption(f"Yahoo Finance | 15-20 min delayed | {stock['timestamp'].strftime('%H:%M:%S')}")

            # Price display
            col1, col2 = st.columns([2, 1])
            with col1:
                chg = "▲" if stock["change"] >= 0 else "▼"
                st.markdown(f"## {stock['ticker']}")
                st.markdown(f"*{stock['name']}*")
                st.metric("Price", f"${stock['price']:.2f}",
                          f"{chg} ${abs(stock['change']):.2f} ({abs(stock['change_pct']):.2f}%)")
            with col2:
                st.metric("Sector", stock["sector"])
                if stock["market_cap"]:
                    cap = stock["market_cap"]
                    cap_str = f"${cap/1e12:.2f}T" if cap >= 1e12 else f"${cap/1e9:.1f}B" if cap >= 1e9 else f"${cap/1e6:.0f}M"
                    st.metric("Market Cap", cap_str)

            st.divider()

            # Key metrics
            st.markdown("### Key Metrics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("P/E Ratio", f"{stock['pe_ratio']:.1f}" if stock['pe_ratio'] else "N/A")
            c2.metric("Beta", f"{stock['beta']:.2f}" if stock['beta'] else "N/A")
            c3.metric("52W High", f"${stock['high_52w']:.2f}" if stock['high_52w'] else "N/A")
            c4.metric("52W Low", f"${stock['low_52w']:.2f}" if stock['low_52w'] else "N/A")

            st.divider()

            # Chart with selectable time range
            st.markdown("### Price Chart")

            periods = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y", "5Y": "5y", "MAX": "max"}
            cols = st.columns(len(periods))

            for i, (label, period) in enumerate(periods.items()):
                with cols[i]:
                    btn_type = "primary" if st.session_state.chart_period == period else "secondary"
                    if st.button(label, key=f"chart_btn_{label}", use_container_width=True, type=btn_type):
                        st.session_state.chart_period = period
                        st.rerun()

            hist = fetch_history(ticker, st.session_state.chart_period)
            if len(hist) > 0:
                st.line_chart(hist["Close"])

                # Period stats
                if len(hist) > 1:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Period High", f"${hist['Close'].max():.2f}")
                    c2.metric("Period Low", f"${hist['Close'].min():.2f}")
                    change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100)
                    c3.metric("Period Change", f"{change:+.1f}%")
                    c4.metric("Volatility", f"{hist['Close'].std():.2f}")
            else:
                st.warning("Chart data unavailable")

            # Show analysis results if available
            if st.session_state.result and ticker in st.session_state.result["ticker_results"]:
                st.divider()
                st.markdown("### From Current Analysis")
                tr = st.session_state.result["ticker_results"][ticker]

                col1, col2 = st.columns(2)
                with col1:
                    if tr["action"] == "BUY":
                        st.success(f"📈 {tr['action']}")
                    elif tr["action"] == "SHORT":
                        st.error(f"📉 {tr['action']}")
                    else:
                        st.warning(f"⏸️ {tr['action']}")
                with col2:
                    st.metric("Confidence", f"{tr['avg_confidence']:.0f}%")

                st.caption(f"**Reason:** {tr['reason']}")

                pos = st.session_state.result["positions"].get(ticker)
                if pos:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Allocation", f"${pos['notional']:,.0f}")
                    c2.metric("Stop Loss", f"${pos['sl_price']:.2f}")
                    c3.metric("Take Profit", f"${pos['tp_price']:.2f}")
        else:
            st.error(f"Could not fetch data for {ticker}")


# ============== SETTINGS TAB ==============
with tab_settings:
    st.subheader("Settings")

    tab_presets, tab_custom = st.tabs(["📊 Risk Presets", "✏️ Custom"])

    with tab_presets:
        st.markdown("### Risk Level Parameter Mapping")

        preset_data = []
        for level in [0.0, 0.25, 0.5, 0.75, 1.0]:
            params = get_risk_params(level)
            label = "Very Conservative" if level == 0 else "Conservative" if level == 0.25 else "Moderate" if level == 0.5 else "Aggressive" if level == 0.75 else "Very Aggressive"
            preset_data.append({
                "Risk": f"{level:.0%} ({label})",
                "Max Position": f"{params['max_position_pct']['value']}%",
                "Stop Loss": f"{params['stop_loss_pct']['value']}%",
                "Take Profit": f"{params['take_profit_pct']['value']}%",
                "Min Confidence": f"{params['min_confidence']['value']}%",
                "Leverage": f"{params['leverage_cap']['value']}x"
            })
        st.dataframe(pd.DataFrame(preset_data), hide_index=True, use_container_width=True)

        with st.expander("Parameter Explanations"):
            st.markdown("""
            - **Max Position**: Maximum % per position. Scales dynamically in Max Deploy mode.
            - **Stop Loss**: Distance from entry to exit on loss.
            - **Take Profit**: Distance from entry to take profit.
            - **Min Confidence**: Minimum analyst confidence to generate a signal.
            - **Leverage**: Maximum leverage allowed.
            """)

    with tab_custom:
        st.markdown("### Custom Parameters")

        use_custom = st.checkbox("Enable custom parameters", value=st.session_state.use_custom)
        st.session_state.use_custom = use_custom

        if use_custom:
            st.warning("Custom parameters override preset values")

            col1, col2 = st.columns(2)
            with col1:
                st.session_state.custom_params["max_position_pct"] = st.number_input(
                    "Max Position %", 5.0, 100.0, float(st.session_state.custom_params.get("max_position_pct", 22.5)), 1.0)
                st.session_state.custom_params["stop_loss_pct"] = st.number_input(
                    "Stop Loss %", 1.0, 50.0, float(st.session_state.custom_params.get("stop_loss_pct", 12.5)), 0.5)
                st.session_state.custom_params["take_profit_pct"] = st.number_input(
                    "Take Profit %", 5.0, 200.0, float(st.session_state.custom_params.get("take_profit_pct", 37.5)), 1.0)
            with col2:
                st.session_state.custom_params["min_confidence"] = st.number_input(
                    "Min Confidence %", 10.0, 90.0, float(st.session_state.custom_params.get("min_confidence", 47.5)), 5.0)
                st.session_state.custom_params["leverage_cap"] = st.number_input(
                    "Leverage Cap", 1.0, 5.0, float(st.session_state.custom_params.get("leverage_cap", 1.5)), 0.1)

            if st.button("Reset to Defaults", use_container_width=True):
                st.session_state.custom_params = {}
                st.session_state.use_custom = False
                st.rerun()
        else:
            st.info("Enable custom parameters to override presets.")


# ============== FOOTER ==============
st.divider()
st.caption("AI Hedge Fund Terminal v4.3 | Educational Use Only | Not Financial Advice")

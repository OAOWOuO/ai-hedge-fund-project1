"""
AI Hedge Fund Terminal v3.0
Professional Trading Dashboard - Fixed Capital Allocation & Sizing Logic
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json

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

    /* Fix button colors - green for primary action */
    .stButton > button[kind="primary"] {
        background-color: #238636 !important;
        border-color: #238636 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2ea043 !important;
        border-color: #2ea043 !important;
    }

    /* High contrast */
    .constraint-binding {
        background: #3d1f1f;
        border-left: 3px solid #f85149;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
    }
    .constraint-ok {
        background: #1f3d1f;
        border-left: 3px solid #3fb950;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ============== ALLOCATION MODES ==============
ALLOCATION_MODES = {
    "fully_allocated": {
        "name": "Fully Allocated",
        "desc": "Deploy most capital across positions (target ~90-95% invested)",
        "target_deployment": 0.95,
        "min_confidence": 30,
        "allow_fractional": False
    },
    "risk_targeted": {
        "name": "Risk Targeted",
        "desc": "Size positions by confidence, may hold significant cash",
        "target_deployment": None,  # No target, let confidence drive
        "min_confidence": 50,
        "allow_fractional": False
    },
    "conservative": {
        "name": "Conservative",
        "desc": "Only high-conviction trades, expect large cash buffer",
        "target_deployment": None,
        "min_confidence": 65,
        "allow_fractional": False
    },
    "equal_weight": {
        "name": "Equal Weight",
        "desc": "Split capital equally among all BUY/SHORT signals",
        "target_deployment": 0.90,
        "min_confidence": 40,
        "allow_fractional": False
    }
}


# ============== DATA CLASSES ==============
@dataclass
class StockData:
    ticker: str
    price: float
    change: float
    change_pct: float
    name: str
    sector: str
    valid: bool
    timestamp: datetime
    source: str = "Yahoo Finance"
    is_delayed: bool = True


@dataclass
class PositionSizing:
    allocated_budget: float      # How much $ was allocated to this ticker
    shares: int                  # Integer shares
    actual_notional: float       # shares * price (actual $ used)
    remainder: float             # allocated - actual (lost to rounding)
    pct_of_portfolio: float      # actual_notional / total_capital


@dataclass
class TradeInstruction:
    ticker: str
    action: str                  # BUY, SELL, SHORT, COVER
    shares: int
    entry_price: float
    notional: float
    stop_loss_price: float
    stop_loss_pct: float
    take_profit_price: float
    take_profit_pct: float
    time_horizon: str
    reason: str


@dataclass
class TickerAnalysis:
    ticker: str
    stock_data: StockData
    signal: str                  # BULLISH, BEARISH, NEUTRAL
    confidence: float
    conviction: float            # % of analysts agreeing
    bullish_count: int
    bearish_count: int
    neutral_count: int
    thesis: str
    key_drivers: List[str]
    risks: List[str]
    analyst_signals: List[Dict]

    # Position details
    recommended_action: str      # BUY, SHORT, HOLD
    sizing: Optional[PositionSizing] = None
    trade: Optional[TradeInstruction] = None

    # For holdings-aware
    current_shares: int = 0
    delta_shares: int = 0        # How many to buy/sell to reach target


@dataclass
class PortfolioAllocation:
    total_capital: float
    deployed_capital: float      # Sum of actual notional
    cash_remaining: float
    deployment_pct: float

    # Breakdown
    long_exposure: float
    short_exposure: float
    gross_exposure: float
    net_exposure: float

    # Rounding losses
    total_rounding_remainder: float

    # Constraints status
    binding_constraints: List[str]

    # Per-ticker
    positions: Dict[str, TickerAnalysis] = field(default_factory=dict)


@dataclass
class RiskParams:
    max_position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    min_confidence: float
    max_sector_pct: float
    leverage_cap: float


# ============== ANALYSTS ==============
ANALYST_CATEGORIES = {
    "Value Investors": {
        "warren_buffett": {"name": "Warren Buffett", "desc": "Moats & quality"},
        "charlie_munger": {"name": "Charlie Munger", "desc": "Mental models"},
        "ben_graham": {"name": "Benjamin Graham", "desc": "Margin of safety"},
    },
    "Growth Investors": {
        "peter_lynch": {"name": "Peter Lynch", "desc": "GARP strategy"},
        "cathie_wood": {"name": "Cathie Wood", "desc": "Disruptive innovation"},
    },
    "Macro & Tactical": {
        "stanley_druckenmiller": {"name": "S. Druckenmiller", "desc": "Macro trends"},
        "ray_dalio": {"name": "Ray Dalio", "desc": "Economic cycles"},
    },
    "Quantitative": {
        "fundamentals_agent": {"name": "Fundamentals", "desc": "Financial ratios"},
        "technical_agent": {"name": "Technical", "desc": "Price patterns"},
        "sentiment_agent": {"name": "Sentiment", "desc": "News analysis"},
        "valuation_agent": {"name": "Valuation", "desc": "DCF models"},
    },
}

def get_all_analysts():
    all_a = {}
    for cat, analysts in ANALYST_CATEGORIES.items():
        for k, v in analysts.items():
            all_a[k] = {**v, "category": cat}
    return all_a


def fetch_stock_data(ticker: str) -> StockData:
    """Fetch stock data."""
    ts = datetime.now()
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        info = stock.info
        if len(hist) >= 1:
            price = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price
            return StockData(
                ticker=ticker, price=price,
                change=price-prev, change_pct=((price-prev)/prev*100) if prev > 0 else 0,
                name=info.get("shortName", ticker), sector=info.get("sector", "Unknown"),
                valid=True, timestamp=ts
            )
    except:
        pass
    return StockData(ticker=ticker, price=0, change=0, change_pct=0, name=ticker,
                     sector="Unknown", valid=False, timestamp=ts)


def calculate_risk_params(risk_level: float) -> RiskParams:
    """Calculate risk parameters."""
    return RiskParams(
        max_position_pct=15 + risk_level * 20,      # 15-35% per position
        stop_loss_pct=15 - risk_level * 10,          # 15-5%
        take_profit_pct=20 + risk_level * 30,        # 20-50%
        min_confidence=60 - risk_level * 25,         # 60-35%
        max_sector_pct=30 + risk_level * 20,         # 30-50%
        leverage_cap=1.0 + risk_level * 1.0          # 1x-2x
    )


def run_analysis(
    tickers: List[str],
    analysts: List[str],
    risk_level: float,
    capital: float,
    holdings: Dict[str, int],
    allocation_mode: str
) -> PortfolioAllocation:
    """
    Run analysis with CORRECT capital allocation.
    """
    # Deterministic seed
    config_str = f"{sorted(tickers)}{sorted(analysts)}{risk_level:.2f}{capital}{allocation_mode}"
    seed = int(hashlib.md5(config_str.encode()).hexdigest()[:8], 16)
    np.random.seed(seed)

    risk_params = calculate_risk_params(risk_level)
    mode_config = ALLOCATION_MODES[allocation_mode]
    all_analysts_info = get_all_analysts()

    # Phase 1: Analyze all tickers
    analyses: Dict[str, TickerAnalysis] = {}

    for ticker in tickers:
        stock = fetch_stock_data(ticker)

        # Generate analyst signals
        analyst_signals = []
        for analyst_key in analysts:
            if analyst_key not in all_analysts_info:
                continue
            info = all_analysts_info[analyst_key]

            # Deterministic signal
            sig_seed = int(hashlib.md5(f"{analyst_key}{ticker}{seed}".encode()).hexdigest()[:8], 16)
            np.random.seed(sig_seed)
            score = np.random.uniform(-1, 1)

            # Analyst bias
            if info["category"] == "Value Investors":
                score -= 0.1
            elif analyst_key == "cathie_wood":
                score += 0.15

            if score > 0.2:
                signal = "BULLISH"
                conf = 55 + score * 35
            elif score < -0.2:
                signal = "BEARISH"
                conf = 55 + abs(score) * 35
            else:
                signal = "NEUTRAL"
                conf = 45 + abs(score) * 15

            analyst_signals.append({
                "analyst": info["name"],
                "category": info["category"],
                "signal": signal,
                "confidence": min(95, max(35, conf))
            })

        # Aggregate
        bullish = sum(1 for s in analyst_signals if s["signal"] == "BULLISH")
        bearish = sum(1 for s in analyst_signals if s["signal"] == "BEARISH")
        neutral = len(analyst_signals) - bullish - bearish
        total = len(analyst_signals)

        avg_conf = np.mean([s["confidence"] for s in analyst_signals]) if analyst_signals else 50

        # Determine signal
        if bullish > bearish and bullish > neutral:
            overall_signal = "BULLISH"
            conviction = bullish / total * 100 if total > 0 else 0
        elif bearish > bullish and bearish > neutral:
            overall_signal = "BEARISH"
            conviction = bearish / total * 100 if total > 0 else 0
        else:
            overall_signal = "NEUTRAL"
            conviction = neutral / total * 100 if total > 0 else 0

        # Recommended action
        if overall_signal == "BULLISH" and avg_conf >= mode_config["min_confidence"]:
            action = "BUY"
        elif overall_signal == "BEARISH" and avg_conf >= mode_config["min_confidence"]:
            action = "SHORT"
        else:
            action = "HOLD"

        # Thesis
        if action == "BUY":
            thesis = f"Bullish consensus ({bullish}/{total}) with {avg_conf:.0f}% confidence exceeds {mode_config['min_confidence']}% threshold."
            drivers = [f"{bullish} analysts bullish", "Confidence above threshold", "Positive momentum indicators"]
            risks = ["Market volatility", "Sector rotation", "Earnings risk"]
        elif action == "SHORT":
            thesis = f"Bearish consensus ({bearish}/{total}) with {avg_conf:.0f}% confidence exceeds {mode_config['min_confidence']}% threshold."
            drivers = [f"{bearish} analysts bearish", "Overvaluation signals", "Negative momentum"]
            risks = ["Short squeeze risk", "Unexpected catalysts", "Timing risk"]
        else:
            thesis = f"No clear consensus ({bullish}B/{neutral}N/{bearish}Be) or confidence {avg_conf:.0f}% below {mode_config['min_confidence']}% threshold."
            drivers = ["Mixed signals", "Insufficient conviction"]
            risks = ["Opportunity cost", "Missing entry point"]

        analyses[ticker] = TickerAnalysis(
            ticker=ticker,
            stock_data=stock,
            signal=overall_signal,
            confidence=avg_conf,
            conviction=conviction,
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            thesis=thesis,
            key_drivers=drivers,
            risks=risks,
            analyst_signals=analyst_signals,
            recommended_action=action,
            current_shares=holdings.get(ticker, 0)
        )

    # Phase 2: Capital Allocation
    actionable = {t: a for t, a in analyses.items() if a.recommended_action != "HOLD" and a.stock_data.valid}

    if not actionable:
        # No actionable signals
        return PortfolioAllocation(
            total_capital=capital,
            deployed_capital=0,
            cash_remaining=capital,
            deployment_pct=0,
            long_exposure=0,
            short_exposure=0,
            gross_exposure=0,
            net_exposure=0,
            total_rounding_remainder=0,
            binding_constraints=["No actionable signals (all HOLD or below confidence threshold)"],
            positions=analyses
        )

    # Allocation strategy based on mode
    target_deployment = mode_config["target_deployment"]

    if allocation_mode == "equal_weight":
        # Equal weight among actionable
        n_positions = len(actionable)
        per_position_budget = (capital * target_deployment) / n_positions

        for ticker, analysis in actionable.items():
            # Cap at max position size
            max_budget = capital * (risk_params.max_position_pct / 100)
            allocated = min(per_position_budget, max_budget)

            price = analysis.stock_data.price
            shares = int(allocated / price)
            actual_notional = shares * price
            remainder = allocated - actual_notional

            analysis.sizing = PositionSizing(
                allocated_budget=allocated,
                shares=shares,
                actual_notional=actual_notional,
                remainder=remainder,
                pct_of_portfolio=(actual_notional / capital * 100)
            )

    elif allocation_mode == "fully_allocated":
        # Allocate proportionally to conviction, targeting ~95% deployment
        total_conviction = sum(a.conviction for a in actionable.values())
        target_deploy = capital * target_deployment

        for ticker, analysis in actionable.items():
            # Weight by conviction
            weight = analysis.conviction / total_conviction if total_conviction > 0 else 1/len(actionable)
            allocated = target_deploy * weight

            # Cap at max position size
            max_budget = capital * (risk_params.max_position_pct / 100)
            allocated = min(allocated, max_budget)

            price = analysis.stock_data.price
            shares = int(allocated / price)
            actual_notional = shares * price
            remainder = allocated - actual_notional

            analysis.sizing = PositionSizing(
                allocated_budget=allocated,
                shares=shares,
                actual_notional=actual_notional,
                remainder=remainder,
                pct_of_portfolio=(actual_notional / capital * 100)
            )

    else:  # risk_targeted or conservative
        # Size by confidence * conviction
        for ticker, analysis in actionable.items():
            # Budget = capital * max_position% * (confidence/100) * (conviction/100)
            confidence_factor = analysis.confidence / 100
            conviction_factor = analysis.conviction / 100

            allocated = capital * (risk_params.max_position_pct / 100) * confidence_factor * conviction_factor

            price = analysis.stock_data.price
            shares = int(allocated / price)
            actual_notional = shares * price
            remainder = allocated - actual_notional

            analysis.sizing = PositionSizing(
                allocated_budget=allocated,
                shares=shares,
                actual_notional=actual_notional,
                remainder=remainder,
                pct_of_portfolio=(actual_notional / capital * 100)
            )

    # Phase 3: Generate Trade Instructions
    for ticker, analysis in analyses.items():
        if analysis.sizing and analysis.sizing.shares > 0:
            price = analysis.stock_data.price
            action = analysis.recommended_action

            # CORRECT stop loss / take profit for LONG vs SHORT
            if action == "BUY":
                sl_price = price * (1 - risk_params.stop_loss_pct / 100)
                tp_price = price * (1 + risk_params.take_profit_pct / 100)
                sl_pct = -risk_params.stop_loss_pct
                tp_pct = risk_params.take_profit_pct
            else:  # SHORT
                sl_price = price * (1 + risk_params.stop_loss_pct / 100)  # ABOVE entry for short
                tp_price = price * (1 - risk_params.take_profit_pct / 100)  # BELOW entry for short
                sl_pct = risk_params.stop_loss_pct  # Loss if price goes UP
                tp_pct = -risk_params.take_profit_pct  # Profit if price goes DOWN

            # Delta from current holdings
            target_shares = analysis.sizing.shares if action == "BUY" else -analysis.sizing.shares
            current = analysis.current_shares
            delta = target_shares - current

            if delta > 0:
                trade_action = "BUY"
            elif delta < 0:
                trade_action = "SELL" if current > 0 else "SHORT"
            else:
                trade_action = "HOLD"

            analysis.delta_shares = delta

            analysis.trade = TradeInstruction(
                ticker=ticker,
                action=trade_action,
                shares=abs(delta),
                entry_price=price,
                notional=abs(delta) * price,
                stop_loss_price=sl_price,
                stop_loss_pct=sl_pct,
                take_profit_price=tp_price,
                take_profit_pct=tp_pct,
                time_horizon="1-3 months" if risk_level < 0.5 else "2-6 weeks",
                reason=f"{'Initiate' if current == 0 else 'Adjust'} position to target"
            )

    # Phase 4: Calculate totals
    long_exp = sum(a.sizing.actual_notional for a in analyses.values()
                   if a.sizing and a.recommended_action == "BUY")
    short_exp = sum(a.sizing.actual_notional for a in analyses.values()
                    if a.sizing and a.recommended_action == "SHORT")
    gross_exp = long_exp + short_exp
    net_exp = long_exp - short_exp
    total_remainder = sum(a.sizing.remainder for a in analyses.values() if a.sizing)

    cash = capital - gross_exp
    deployment_pct = (gross_exp / capital * 100) if capital > 0 else 0

    # Identify binding constraints
    binding = []
    if deployment_pct < 50:
        if allocation_mode in ["risk_targeted", "conservative"]:
            binding.append(f"Risk-targeted mode: Confidence-based sizing deployed {deployment_pct:.1f}%")
        else:
            binding.append(f"Limited actionable signals: Only {len(actionable)} of {len(tickers)} tickers met confidence threshold")

    if any(a.sizing and a.sizing.pct_of_portfolio >= risk_params.max_position_pct * 0.95 for a in analyses.values()):
        binding.append(f"Max position size cap ({risk_params.max_position_pct:.0f}%) binding on some positions")

    if not binding:
        binding.append("No constraints binding - full allocation achieved")

    return PortfolioAllocation(
        total_capital=capital,
        deployed_capital=gross_exp,
        cash_remaining=cash,
        deployment_pct=deployment_pct,
        long_exposure=long_exp,
        short_exposure=short_exp,
        gross_exposure=gross_exp,
        net_exposure=net_exp,
        total_rounding_remainder=total_remainder,
        binding_constraints=binding,
        positions=analyses
    )


# ============== SESSION STATE ==============
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Signals"
if "result" not in st.session_state:
    st.session_state.result = None
if "selected_analysts" not in st.session_state:
    st.session_state.selected_analysts = list(get_all_analysts().keys())[:6]


# ============== HEADER ==============
st.markdown("## 📊 AI Hedge Fund Terminal")

if st.session_state.result:
    st.caption(f"Data: Yahoo Finance (Delayed 15-20 min) | Last run: {datetime.now().strftime('%H:%M:%S')}")

# Navigation
tabs = ["Signals", "Portfolio", "Trade List"]
selected = st.radio("", tabs, horizontal=True, label_visibility="collapsed")
st.session_state.active_tab = selected

st.divider()


# ============== SIGNALS PAGE ==============
if st.session_state.active_tab == "Signals":

    config_col, results_col = st.columns([1, 2])

    with config_col:
        st.subheader("⚙️ Configuration")

        # Tickers
        st.markdown("**Tickers**")
        ticker_input = st.text_input("Enter tickers", value="AAPL, MSFT, NVDA, GOOGL",
                                      label_visibility="collapsed")
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        st.divider()

        # Capital
        st.markdown("**Investment Capital**")
        capital = st.number_input("Capital ($)", min_value=1000, value=100000, step=5000,
                                   label_visibility="collapsed")

        # Holdings
        st.markdown("**Current Holdings** (optional)")
        holdings_text = st.text_area("TICKER:SHARES", placeholder="AAPL:50\nMSFT:30",
                                      height=80, label_visibility="collapsed")
        holdings = {}
        for line in holdings_text.strip().split("\n"):
            if ":" in line:
                try:
                    t, s = line.split(":")
                    holdings[t.strip().upper()] = int(s.strip())
                except:
                    pass

        st.divider()

        # Allocation Mode
        st.markdown("**Allocation Mode**")
        mode = st.selectbox(
            "Mode",
            options=list(ALLOCATION_MODES.keys()),
            format_func=lambda x: ALLOCATION_MODES[x]["name"],
            label_visibility="collapsed"
        )
        st.caption(ALLOCATION_MODES[mode]["desc"])

        st.divider()

        # Risk Level
        st.markdown("**Risk Level**")
        risk_level = st.slider("Risk", 0.0, 1.0, 0.5, 0.05, label_visibility="collapsed")

        risk_params = calculate_risk_params(risk_level)
        risk_label = "Conservative" if risk_level < 0.35 else "Aggressive" if risk_level > 0.65 else "Moderate"

        st.markdown(f"**{risk_label}** ({risk_level:.0%})")

        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Max Position: {risk_params.max_position_pct:.0f}%")
            st.caption(f"Stop Loss: {risk_params.stop_loss_pct:.0f}%")
        with col2:
            st.caption(f"Take Profit: {risk_params.take_profit_pct:.0f}%")
            st.caption(f"Min Confidence: {risk_params.min_confidence:.0f}%")

        st.divider()

        # Analysts
        st.markdown("**AI Analysts**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Select All", use_container_width=True):
                st.session_state.selected_analysts = list(get_all_analysts().keys())
                st.rerun()
        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_analysts = []
                st.rerun()

        for cat, analysts in ANALYST_CATEGORIES.items():
            with st.expander(f"{cat}"):
                for key, info in analysts.items():
                    if st.checkbox(info["name"], value=key in st.session_state.selected_analysts, key=f"a_{key}"):
                        if key not in st.session_state.selected_analysts:
                            st.session_state.selected_analysts.append(key)
                    else:
                        if key in st.session_state.selected_analysts:
                            st.session_state.selected_analysts.remove(key)

        st.caption(f"{len(st.session_state.selected_analysts)} analysts selected")

        st.divider()

        # Run button - GREEN not red
        if st.button("🚀 RUN ANALYSIS", type="primary", use_container_width=True,
                     disabled=len(tickers) == 0 or len(st.session_state.selected_analysts) == 0):
            with st.spinner("Analyzing..."):
                st.session_state.result = run_analysis(
                    tickers, st.session_state.selected_analysts,
                    risk_level, capital, holdings, mode
                )
            st.rerun()

    # Results
    with results_col:
        if st.session_state.result:
            r = st.session_state.result

            # CAPITAL ALLOCATION BREAKDOWN - THE KEY FIX
            st.subheader("💰 Capital Allocation")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Capital", f"${r.total_capital:,.0f}")
            with col2:
                st.metric("Deployed", f"${r.deployed_capital:,.0f}",
                         f"{r.deployment_pct:.1f}%")
            with col3:
                st.metric("Cash Remaining", f"${r.cash_remaining:,.0f}",
                         f"{100-r.deployment_pct:.1f}%")
            with col4:
                st.metric("Rounding Loss", f"${r.total_rounding_remainder:,.0f}",
                         help="Lost to integer share rounding")

            # Binding constraints - EXPLAIN WHY CASH REMAINS
            st.markdown("**Why this allocation?**")
            for constraint in r.binding_constraints:
                if "binding" in constraint.lower() or "limited" in constraint.lower() or "risk" in constraint.lower():
                    st.markdown(f'<div class="constraint-binding">⚠️ {constraint}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="constraint-ok">✅ {constraint}</div>', unsafe_allow_html=True)

            st.divider()

            # Exposure breakdown
            st.subheader("📊 Exposure")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Long", f"${r.long_exposure:,.0f}")
            with col2:
                st.metric("Short", f"${r.short_exposure:,.0f}")
            with col3:
                st.metric("Gross", f"${r.gross_exposure:,.0f}")
            with col4:
                st.metric("Net", f"${r.net_exposure:,.0f}")

            st.divider()

            # Per-ticker cards
            st.subheader("📈 Recommendations")

            for ticker, analysis in r.positions.items():
                stock = analysis.stock_data

                # Header
                col1, col2 = st.columns([3, 1])
                with col1:
                    price_str = f"${stock.price:.2f}" if stock.valid else "N/A"
                    change_str = f"{'▲' if stock.change >= 0 else '▼'} {abs(stock.change_pct):.2f}%" if stock.valid else ""
                    st.markdown(f"### {ticker} - {price_str} {change_str}")
                    st.caption(f"{stock.name} | {stock.source} | {stock.timestamp.strftime('%H:%M:%S')}")
                with col2:
                    if analysis.recommended_action == "BUY":
                        st.success(f"📈 {analysis.recommended_action}")
                    elif analysis.recommended_action == "SHORT":
                        st.error(f"📉 {analysis.recommended_action}")
                    else:
                        st.warning(f"➡️ {analysis.recommended_action}")

                # Thesis
                st.info(analysis.thesis)

                # Sizing details - SHOW BUDGET vs ACTUAL vs REMAINDER
                if analysis.sizing and analysis.sizing.shares > 0:
                    st.markdown("**Position Sizing:**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Allocated Budget", f"${analysis.sizing.allocated_budget:,.0f}")
                    with col2:
                        st.metric("Shares", f"{analysis.sizing.shares:,}")
                    with col3:
                        st.metric("Actual Notional", f"${analysis.sizing.actual_notional:,.0f}")
                    with col4:
                        st.metric("Remainder", f"${analysis.sizing.remainder:,.2f}",
                                 help="Budget not used due to integer shares")

                    st.caption(f"Position = {analysis.sizing.pct_of_portfolio:.1f}% of portfolio")

                # Trade instruction with CORRECT SL/TP for long vs short
                if analysis.trade:
                    t = analysis.trade
                    st.markdown("**Trade Instruction:**")

                    # Show delta if holdings exist
                    if analysis.current_shares != 0:
                        st.caption(f"Current: {analysis.current_shares} shares → Target: {analysis.sizing.shares if analysis.sizing else 0} → Delta: {analysis.delta_shares:+d}")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Action", f"{t.action} {t.shares}")
                    with col2:
                        st.metric("Entry", f"${t.entry_price:.2f}")
                    with col3:
                        # CORRECT labeling for SHORT
                        if analysis.recommended_action == "SHORT":
                            st.metric("Stop Loss", f"${t.stop_loss_price:.2f}",
                                     f"+{t.stop_loss_pct:.1f}% (above entry)",
                                     delta_color="inverse",
                                     help="For SHORT: Stop loss is ABOVE entry - exit if price rises")
                        else:
                            st.metric("Stop Loss", f"${t.stop_loss_price:.2f}",
                                     f"{t.stop_loss_pct:.1f}% (below entry)",
                                     help="For LONG: Stop loss is BELOW entry - exit if price falls")
                    with col4:
                        if analysis.recommended_action == "SHORT":
                            st.metric("Take Profit", f"${t.take_profit_price:.2f}",
                                     f"{t.take_profit_pct:.1f}% (below entry)",
                                     help="For SHORT: Take profit is BELOW entry - exit when price falls")
                        else:
                            st.metric("Take Profit", f"${t.take_profit_price:.2f}",
                                     f"+{t.take_profit_pct:.1f}% (above entry)",
                                     help="For LONG: Take profit is ABOVE entry - exit when price rises")

                # Vote breakdown
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", f"{analysis.confidence:.0f}%")
                with col2:
                    st.metric("Bullish", analysis.bullish_count)
                with col3:
                    st.metric("Neutral", analysis.neutral_count)
                with col4:
                    st.metric("Bearish", analysis.bearish_count)

                # Key drivers & risks
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Drivers:**")
                    for d in analysis.key_drivers:
                        st.caption(f"• {d}")
                with col2:
                    st.markdown("**Risks:**")
                    for risk in analysis.risks:
                        st.caption(f"• {risk}")

                # Analyst breakdown
                with st.expander(f"View {len(analysis.analyst_signals)} analyst signals"):
                    for sig in analysis.analyst_signals:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.text(f"{sig['analyst']} ({sig['category']})")
                        with col2:
                            if sig['signal'] == "BULLISH":
                                st.success(sig['signal'])
                            elif sig['signal'] == "BEARISH":
                                st.error(sig['signal'])
                            else:
                                st.warning(sig['signal'])
                        with col3:
                            st.text(f"{sig['confidence']:.0f}%")

                st.divider()

        else:
            st.markdown("""
            ### 👈 Configure & Run

            1. Enter tickers
            2. Set capital amount
            3. Choose allocation mode:
               - **Fully Allocated**: Deploy ~95% of capital
               - **Equal Weight**: Split evenly among signals
               - **Risk Targeted**: Size by confidence (may hold cash)
               - **Conservative**: Only high-conviction trades
            4. Adjust risk level
            5. Select analysts
            6. Click **RUN ANALYSIS**
            """)


# ============== PORTFOLIO PAGE ==============
elif st.session_state.active_tab == "Portfolio":
    st.subheader("💼 Portfolio Summary")

    if st.session_state.result:
        r = st.session_state.result

        # Summary table
        positions = []
        for ticker, a in r.positions.items():
            if a.sizing:
                positions.append({
                    "Ticker": ticker,
                    "Action": a.recommended_action,
                    "Shares": a.sizing.shares,
                    "Entry": f"${a.stock_data.price:.2f}",
                    "Notional": f"${a.sizing.actual_notional:,.0f}",
                    "% Portfolio": f"{a.sizing.pct_of_portfolio:.1f}%",
                    "Stop Loss": f"${a.trade.stop_loss_price:.2f}" if a.trade else "N/A",
                    "Take Profit": f"${a.trade.take_profit_price:.2f}" if a.trade else "N/A",
                })

        if positions:
            st.dataframe(pd.DataFrame(positions), hide_index=True, use_container_width=True)
        else:
            st.info("No positions. All tickers are HOLD.")

        st.divider()

        # Cash breakdown
        st.markdown("### 💵 Cash Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Unallocated Cash", f"${r.cash_remaining:,.0f}")
        with col2:
            st.metric("Rounding Remainders", f"${r.total_rounding_remainder:,.0f}")
        with col3:
            st.metric("Total Uninvested", f"${r.cash_remaining + r.total_rounding_remainder:,.0f}")
    else:
        st.info("Run analysis first.")


# ============== TRADE LIST PAGE ==============
elif st.session_state.active_tab == "Trade List":
    st.subheader("📋 Trade Instructions")

    if st.session_state.result:
        r = st.session_state.result

        trades = []
        for ticker, a in r.positions.items():
            if a.trade and a.trade.shares > 0:
                trades.append({
                    "Ticker": ticker,
                    "Action": a.trade.action,
                    "Shares": a.trade.shares,
                    "Entry Price": f"${a.trade.entry_price:.2f}",
                    "Notional": f"${a.trade.notional:,.0f}",
                    "Stop Loss": f"${a.trade.stop_loss_price:.2f}",
                    "Take Profit": f"${a.trade.take_profit_price:.2f}",
                    "Horizon": a.trade.time_horizon
                })

        if trades:
            st.dataframe(pd.DataFrame(trades), hide_index=True, use_container_width=True)

            st.divider()
            st.markdown("**Execution Notes:**")
            st.caption("• All prices are delayed 15-20 minutes (Yahoo Finance)")
            st.caption("• Use limit orders at or near indicated entry prices")
            st.caption("• Set stop losses immediately after entry")
            st.caption("• Review positions daily and adjust as needed")
        else:
            st.info("No trades required. All positions are HOLD or already at target.")
    else:
        st.info("Run analysis first.")


# ============== FOOTER ==============
st.divider()
st.caption("AI Hedge Fund Terminal | Educational Use Only | Not Financial Advice")
st.caption("Data: Yahoo Finance (delayed 15-20 min) | Past performance ≠ future results")

"""
AI → Options Bridge

Connects AI agent stock signals to options trading opportunities.
Converts bullish signals into cash-secured put opportunities.
Converts assigned positions into covered call opportunities.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Literal
from dateutil.relativedelta import relativedelta
import pandas as pd

from src.main import run_hedge_fund
from src.utils.analysts import ANALYST_CONFIG
from src.options.data import get_options_chain
from src.options.filters import find_optimal_strike, OptimalStrike


@dataclass
class AgentSignal:
    """Parsed signal from an AI agent."""
    ticker: str
    agent_name: str
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: int  # 0-100
    reasoning: str


@dataclass
class OptionsOpportunity:
    """An options trade opportunity based on AI signals."""
    ticker: str
    action: Literal["SELL_PUT", "SELL_CALL"]
    strike: float
    expiration: date
    premium: float
    delta: float
    theta: float
    iv: float
    dte: int
    annual_yield: float
    breakeven: float

    # AI signal data
    signal_strength: str  # "strong", "moderate", "weak"
    consensus_confidence: float  # Average confidence from agents
    bullish_agents: int
    total_agents: int

    # Reasoning
    rationale: str

    def __repr__(self) -> str:
        return f"OptionsOpportunity({self.action} {self.ticker} ${self.strike} @ ${self.premium:.2f}, Δ={self.delta:.2f}, yield={self.annual_yield*100:.1f}%)"


def run_ai_analysis(
    tickers: list[str],
    selected_analysts: Optional[list[str]] = None,
    model_name: str = "gpt-4o-mini",
    model_provider: str = "OpenAI",
    show_reasoning: bool = False,
) -> dict:
    """
    Run AI agents on a list of tickers.

    Args:
        tickers: List of stock symbols
        selected_analysts: List of analyst keys to use (None = all)
        model_name: LLM model to use
        model_provider: LLM provider
        show_reasoning: Whether to print agent reasoning

    Returns:
        Dict with 'decisions' and 'analyst_signals'
    """
    # Set up date range (analyze recent data)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - relativedelta(months=3)).strftime("%Y-%m-%d")

    # Create portfolio structure (required by run_hedge_fund)
    portfolio = {
        "cash": 100000,
        "margin_requirement": 0.0,
        "margin_used": 0.0,
        "positions": {
            ticker: {
                "long": 0,
                "short": 0,
                "long_cost_basis": 0.0,
                "short_cost_basis": 0.0,
                "short_margin_used": 0.0,
            }
            for ticker in tickers
        },
        "realized_gains": {
            ticker: {"long": 0.0, "short": 0.0}
            for ticker in tickers
        },
    }

    # Run the hedge fund analysis
    result = run_hedge_fund(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        portfolio=portfolio,
        show_reasoning=show_reasoning,
        selected_analysts=selected_analysts or [],
        model_name=model_name,
        model_provider=model_provider,
    )

    return result


def parse_agent_signals(analyst_signals: dict) -> list[AgentSignal]:
    """
    Parse raw analyst signals into structured AgentSignal objects.

    Args:
        analyst_signals: Dict from run_hedge_fund result

    Returns:
        List of AgentSignal objects
    """
    signals = []

    for agent_key, ticker_signals in analyst_signals.items():
        # Get display name from config
        agent_name = agent_key.replace("_agent", "")
        display_name = ANALYST_CONFIG.get(agent_name, {}).get("display_name", agent_key)

        for ticker, signal_data in ticker_signals.items():
            if isinstance(signal_data, dict):
                signals.append(AgentSignal(
                    ticker=ticker,
                    agent_name=display_name,
                    signal=signal_data.get("signal", "neutral"),
                    confidence=signal_data.get("confidence", 0),
                    reasoning=signal_data.get("reasoning", ""),
                ))

    return signals


def aggregate_signals_by_ticker(signals: list[AgentSignal]) -> dict[str, dict]:
    """
    Aggregate signals from multiple agents for each ticker.

    Returns dict with:
        - consensus: "bullish", "bearish", "neutral"
        - avg_confidence: average confidence of consensus signals
        - bullish_count, bearish_count, neutral_count
        - total_agents
        - agents: list of agent signals
    """
    ticker_data = {}

    for signal in signals:
        if signal.ticker not in ticker_data:
            ticker_data[signal.ticker] = {
                "bullish": [],
                "bearish": [],
                "neutral": [],
                "agents": [],
            }

        ticker_data[signal.ticker][signal.signal].append(signal)
        ticker_data[signal.ticker]["agents"].append(signal)

    # Determine consensus for each ticker
    result = {}
    for ticker, data in ticker_data.items():
        bullish_count = len(data["bullish"])
        bearish_count = len(data["bearish"])
        neutral_count = len(data["neutral"])
        total = bullish_count + bearish_count + neutral_count

        # Consensus is the majority signal
        if bullish_count > bearish_count and bullish_count > neutral_count:
            consensus = "bullish"
            consensus_signals = data["bullish"]
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            consensus = "bearish"
            consensus_signals = data["bearish"]
        else:
            consensus = "neutral"
            consensus_signals = data["neutral"]

        # Average confidence of consensus signals
        avg_confidence = (
            sum(s.confidence for s in consensus_signals) / len(consensus_signals)
            if consensus_signals else 0
        )

        result[ticker] = {
            "consensus": consensus,
            "avg_confidence": avg_confidence,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "total_agents": total,
            "agents": data["agents"],
        }

    return result


def generate_options_opportunities(
    tickers: list[str],
    selected_analysts: Optional[list[str]] = None,
    min_confidence: float = 60.0,
    delta_target: float = 0.25,
    min_dte: int = 20,
    max_dte: int = 50,
    model_name: str = "gpt-4o-mini",
    model_provider: str = "OpenAI",
    show_reasoning: bool = False,
) -> list[OptionsOpportunity]:
    """
    Generate options opportunities from AI agent analysis.

    Args:
        tickers: List of stock symbols to analyze
        selected_analysts: Analyst keys to use (None = all)
        min_confidence: Minimum consensus confidence to consider (0-100)
        delta_target: Target delta for strike selection
        min_dte: Minimum days to expiration
        max_dte: Maximum days to expiration
        model_name: LLM model
        model_provider: LLM provider
        show_reasoning: Print agent reasoning

    Returns:
        List of OptionsOpportunity for bullish signals
    """
    print(f"\n[1] Running AI analysis on {len(tickers)} tickers...")

    # Run AI analysis
    result = run_ai_analysis(
        tickers=tickers,
        selected_analysts=selected_analysts,
        model_name=model_name,
        model_provider=model_provider,
        show_reasoning=show_reasoning,
    )

    # Parse and aggregate signals
    print("[2] Parsing agent signals...")
    signals = parse_agent_signals(result.get("analyst_signals", {}))
    aggregated = aggregate_signals_by_ticker(signals)

    # Filter for bullish signals with sufficient confidence
    print(f"[3] Filtering for bullish signals (confidence >= {min_confidence}%)...")
    bullish_tickers = [
        (ticker, data)
        for ticker, data in aggregated.items()
        if data["consensus"] == "bullish" and data["avg_confidence"] >= min_confidence
    ]

    if not bullish_tickers:
        print("    No bullish signals found meeting criteria.")
        return []

    print(f"    Found {len(bullish_tickers)} bullish tickers")

    # Generate options opportunities
    print("[4] Generating options opportunities...")
    opportunities = []

    for ticker, signal_data in bullish_tickers:
        try:
            # Get options chain
            chain = get_options_chain(ticker, min_dte=min_dte, max_dte=max_dte)

            # Find optimal put to sell
            optimal = find_optimal_strike(chain.puts, "put", target_delta=delta_target)

            if optimal is None:
                print(f"    {ticker}: No suitable strikes found")
                continue

            # Determine signal strength
            confidence = signal_data["avg_confidence"]
            if confidence >= 80:
                strength = "strong"
            elif confidence >= 70:
                strength = "moderate"
            else:
                strength = "weak"

            # Create opportunity
            opportunity = OptionsOpportunity(
                ticker=ticker,
                action="SELL_PUT",
                strike=optimal.strike,
                expiration=chain.expiration,
                premium=optimal.premium,
                delta=optimal.delta,
                theta=optimal.theta,
                iv=optimal.iv,
                dte=optimal.dte,
                annual_yield=optimal.annual_return,
                breakeven=optimal.breakeven,
                signal_strength=strength,
                consensus_confidence=confidence,
                bullish_agents=signal_data["bullish_count"],
                total_agents=signal_data["total_agents"],
                rationale=f"{signal_data['bullish_count']}/{signal_data['total_agents']} agents bullish with {confidence:.0f}% avg confidence. {optimal.reason}",
            )

            opportunities.append(opportunity)
            print(f"    {ticker}: SELL ${optimal.strike} PUT @ ${optimal.premium:.2f} ({optimal.annual_return*100:.1f}% yield)")

        except Exception as e:
            print(f"    {ticker}: Error - {e}")
            continue

    return opportunities


def opportunities_to_dataframe(opportunities: list[OptionsOpportunity]) -> pd.DataFrame:
    """Convert list of opportunities to a pandas DataFrame for display."""
    if not opportunities:
        return pd.DataFrame()

    data = []
    for opp in opportunities:
        data.append({
            "Ticker": opp.ticker,
            "Action": opp.action,
            "Strike": opp.strike,
            "Premium": opp.premium,
            "Delta": opp.delta,
            "DTE": opp.dte,
            "Annual Yield": f"{opp.annual_yield*100:.1f}%",
            "Breakeven": opp.breakeven,
            "Signal": opp.signal_strength,
            "Confidence": f"{opp.consensus_confidence:.0f}%",
            "Agents": f"{opp.bullish_agents}/{opp.total_agents}",
        })

    return pd.DataFrame(data)


def get_analyst_keys() -> list[str]:
    """Get list of available analyst keys."""
    return list(ANALYST_CONFIG.keys())


def get_analyst_info() -> list[dict]:
    """Get info about all available analysts."""
    return [
        {
            "key": key,
            "name": config["display_name"],
            "style": config["investing_style"],
        }
        for key, config in ANALYST_CONFIG.items()
    ]

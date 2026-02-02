#!/usr/bin/env python3
"""
Simplified demo for Section 2: AI → Options Bridge

Shows the bridge structure with mock signals (no API dependency).

Run: poetry run python src/options/demo_bridge_simple.py
"""

from datetime import date
from src.options.data import get_options_chain
from src.options.filters import find_optimal_strike
from src.options.bridge import OptionsOpportunity, opportunities_to_dataframe


def create_mock_signals():
    """
    Create mock AI signals to demonstrate the bridge.
    In production, these come from run_ai_analysis().
    """
    return {
        "NVDA": {
            "consensus": "bullish",
            "avg_confidence": 78.0,
            "bullish_count": 4,
            "total_agents": 5,
            "reasoning": "Strong AI demand, dominant GPU market position, high margins",
        },
        "AAPL": {
            "consensus": "bullish",
            "avg_confidence": 72.0,
            "bullish_count": 3,
            "total_agents": 5,
            "reasoning": "Services growth, strong ecosystem, solid cash flow",
        },
        "MSFT": {
            "consensus": "bullish",
            "avg_confidence": 82.0,
            "bullish_count": 4,
            "total_agents": 5,
            "reasoning": "Azure growth, AI integration, enterprise dominance",
        },
        "TSLA": {
            "consensus": "neutral",
            "avg_confidence": 45.0,
            "bullish_count": 2,
            "total_agents": 5,
            "reasoning": "Mixed signals on demand, high valuation concerns",
        },
    }


def generate_opportunities_from_signals(
    signals: dict,
    min_confidence: float = 60.0,
    delta_target: float = 0.25,
) -> list[OptionsOpportunity]:
    """
    Convert mock signals to options opportunities.
    """
    opportunities = []

    # Filter for bullish signals with sufficient confidence
    bullish_tickers = [
        (ticker, data)
        for ticker, data in signals.items()
        if data["consensus"] == "bullish" and data["avg_confidence"] >= min_confidence
    ]

    for ticker, signal_data in bullish_tickers:
        try:
            # Get real options chain
            chain = get_options_chain(ticker, min_dte=20, max_dte=50)

            # Find optimal put to sell
            optimal = find_optimal_strike(chain.puts, "put", target_delta=delta_target)

            if optimal is None:
                print(f"    {ticker}: No suitable strikes found")
                continue

            # Determine signal strength
            confidence = signal_data["avg_confidence"]
            strength = "strong" if confidence >= 80 else "moderate" if confidence >= 70 else "weak"

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
                rationale=f"{signal_data['bullish_count']}/{signal_data['total_agents']} agents bullish. {signal_data['reasoning']}",
            )

            opportunities.append(opportunity)

        except Exception as e:
            print(f"    {ticker}: Error - {e}")

    return opportunities


def main():
    print(f"\n{'='*70}")
    print(f"  AI → OPTIONS BRIDGE DEMO (Simplified)")
    print(f"{'='*70}\n")

    # Step 1: Mock AI signals (in production, from run_ai_analysis)
    print("[1] Simulating AI agent signals...")
    signals = create_mock_signals()

    for ticker, data in signals.items():
        status = "✓" if data["consensus"] == "bullish" and data["avg_confidence"] >= 60 else "✗"
        print(f"    {status} {ticker}: {data['consensus'].upper()} ({data['avg_confidence']:.0f}% confidence)")

    # Step 2: Filter bullish signals
    print("\n[2] Filtering for bullish signals (confidence >= 60%)...")
    bullish = [(t, d) for t, d in signals.items()
               if d["consensus"] == "bullish" and d["avg_confidence"] >= 60]
    print(f"    Found {len(bullish)} qualifying tickers: {[t for t, _ in bullish]}")

    # Step 3: Generate options opportunities
    print("\n[3] Generating options opportunities...")
    opportunities = generate_opportunities_from_signals(signals, min_confidence=60.0)

    # Step 4: Display results
    print(f"\n{'='*70}")
    print(f"  OPPORTUNITIES FOUND: {len(opportunities)}")
    print(f"{'='*70}\n")

    if opportunities:
        df = opportunities_to_dataframe(opportunities)
        print(df.to_string(index=False))

        print("\n" + "─"*70)
        print("TRADE RECOMMENDATIONS:")
        print("─"*70)

        for opp in opportunities:
            print(f"\n┌─ {opp.ticker}: {opp.action.replace('_', ' ')} ─────────────────────")
            print(f"│  Strike:      ${opp.strike:.0f}")
            print(f"│  Premium:     ${opp.premium:.2f} (${opp.premium*100:.0f}/contract)")
            print(f"│  Delta:       {opp.delta:.3f} ({abs(opp.delta)*100:.0f}% ITM probability)")
            print(f"│  Expiration:  {opp.expiration} ({opp.dte} days)")
            print(f"│  Breakeven:   ${opp.breakeven:.2f}")
            print(f"│  Ann. Yield:  {opp.annual_yield*100:.1f}%")
            print(f"│  AI Signal:   {opp.signal_strength.upper()} ({opp.consensus_confidence:.0f}%)")
            print(f"│  Agents:      {opp.bullish_agents}/{opp.total_agents} bullish")
            print(f"└─ Rationale:   {opp.rationale[:60]}...")

    print(f"\n{'='*70}")
    print("  SECTION 2 COMPLETE - AI → Options Bridge Working!")
    print(f"{'='*70}")
    print("\n  Next: Section 3 (Wheel State Machine) will track position lifecycle")
    print("        from PUT_SOLD → ASSIGNED → CALL_SOLD → CALLED_AWAY\n")


if __name__ == "__main__":
    main()

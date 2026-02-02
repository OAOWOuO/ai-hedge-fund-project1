#!/usr/bin/env python3
"""
Demo script for Section 2: AI → Options Bridge

Runs AI agents on tickers and generates options opportunities.

Run: poetry run python src/options/demo_bridge.py
"""

from dotenv import load_dotenv
load_dotenv()

from src.options.bridge import (
    generate_options_opportunities,
    opportunities_to_dataframe,
    get_analyst_info,
)


def main():
    print(f"\n{'='*70}")
    print(f"  AI → OPTIONS BRIDGE DEMO")
    print(f"{'='*70}\n")

    # Configuration
    tickers = ["NVDA", "AAPL", "MSFT"]  # Test with 3 tickers

    # Use a subset of analysts for faster demo (value investors)
    selected_analysts = [
        "warren_buffett",
        "charlie_munger",
        "ben_graham",
        "fundamentals_analyst",
        "valuation_analyst",
    ]

    print("Configuration:")
    print(f"  Tickers: {tickers}")
    print(f"  Analysts: {len(selected_analysts)} selected")
    for key in selected_analysts:
        print(f"    - {key}")
    print(f"  Min Confidence: 50%")
    print(f"  Target Delta: 0.25")
    print()

    # Generate opportunities
    opportunities = generate_options_opportunities(
        tickers=tickers,
        selected_analysts=selected_analysts,
        min_confidence=50.0,  # Lower threshold for demo
        delta_target=0.25,
        min_dte=20,
        max_dte=50,
        model_name="gpt-4o-mini",  # Fast and cheap for demo
        model_provider="OpenAI",
        show_reasoning=False,
    )

    # Display results
    print(f"\n{'='*70}")
    print(f"  OPPORTUNITIES FOUND: {len(opportunities)}")
    print(f"{'='*70}\n")

    if opportunities:
        df = opportunities_to_dataframe(opportunities)
        print(df.to_string(index=False))

        print("\n" + "─"*70)
        print("DETAILED RECOMMENDATIONS:")
        print("─"*70)

        for opp in opportunities:
            print(f"\n{opp.ticker}: {opp.action.replace('_', ' ')}")
            print(f"  Strike:      ${opp.strike:.0f}")
            print(f"  Premium:     ${opp.premium:.2f} (${opp.premium*100:.0f}/contract)")
            print(f"  Delta:       {opp.delta:.3f}")
            print(f"  Expiration:  {opp.expiration} ({opp.dte} days)")
            print(f"  Breakeven:   ${opp.breakeven:.2f}")
            print(f"  Ann. Yield:  {opp.annual_yield*100:.1f}%")
            print(f"  Signal:      {opp.signal_strength.upper()} ({opp.consensus_confidence:.0f}% confidence)")
            print(f"  Rationale:   {opp.rationale}")
    else:
        print("No opportunities found. Try:")
        print("  - Lowering min_confidence threshold")
        print("  - Adding more tickers")
        print("  - Using different analysts")

    print(f"\n{'='*70}")
    print("  SECTION 2 COMPLETE - AI → Options Bridge Working!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

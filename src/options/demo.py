#!/usr/bin/env python3
"""
Demo script for Section 1: Options Data Layer

Run: poetry run python src/options/demo.py
"""

from src.options.data import get_options_chain, get_expirations
from src.options.greeks import calculate_greeks, add_greeks_to_chain
from src.options.filters import filter_by_delta, find_optimal_strike, rank_strikes_for_income


def main():
    ticker = "NVDA"
    print(f"\n{'='*60}")
    print(f"  OPTIONS DATA LAYER DEMO - {ticker}")
    print(f"{'='*60}\n")

    # 1. Fetch options chain
    print("[1] Fetching options chain...")
    chain = get_options_chain(ticker, min_dte=20, max_dte=50)
    print(f"    Ticker: {chain.ticker}")
    print(f"    Underlying: ${chain.underlying_price:.2f}")
    print(f"    Expiration: {chain.expiration}")
    print(f"    Calls: {len(chain.calls)} strikes")
    print(f"    Puts: {len(chain.puts)} strikes")

    # 2. Add Greeks to puts
    print("\n[2] Calculating Greeks for puts...")
    puts_with_greeks = add_greeks_to_chain(chain.puts, "put")
    print(f"    Added delta, gamma, theta, vega columns")

    # 3. Filter by delta (0.20-0.30 range for income)
    print("\n[3] Filtering puts by delta (0.20-0.30)...")
    filtered = filter_by_delta(chain.puts, "put", min_delta=0.20, max_delta=0.30)
    print(f"    Found {len(filtered)} strikes in range\n")

    if not filtered.empty:
        cols = ["strike", "bid", "ask", "mid_price", "delta", "theta", "impliedVolatility"]
        available_cols = [c for c in cols if c in filtered.columns]
        print(filtered[available_cols].head(5).to_string(index=False))

    # 4. Find optimal strike
    print("\n[4] Finding optimal strike for cash-secured put (target Δ=0.25)...")
    optimal = find_optimal_strike(chain.puts, "put", target_delta=0.25)

    if optimal:
        print(f"\n    RECOMMENDATION: Sell {ticker} ${optimal.strike:.0f} Put")
        print(f"    ─────────────────────────────────")
        print(f"    Premium:      ${optimal.premium:.2f} (${optimal.bid:.2f} bid / ${optimal.ask:.2f} ask)")
        print(f"    Delta:        {optimal.delta:.3f} ({abs(optimal.delta)*100:.0f}% probability ITM)")
        print(f"    Theta:        ${optimal.theta:.3f}/day decay")
        print(f"    IV:           {optimal.iv*100:.1f}%")
        print(f"    DTE:          {optimal.dte} days")
        print(f"    Breakeven:    ${optimal.breakeven:.2f}")
        print(f"    Annual Yield: {optimal.annual_return*100:.1f}%")
        print(f"    Rationale:    {optimal.reason}")

    # 5. Rank top strikes for income
    print("\n[5] Top 5 strikes ranked by income score...")
    ranked = rank_strikes_for_income(chain.puts, "put", top_n=5)

    if not ranked.empty:
        print()
        # Format for display
        display_df = ranked.copy()
        display_df["delta"] = display_df["delta"].apply(lambda x: f"{x:.3f}")
        display_df["yield"] = display_df["yield"].apply(lambda x: f"{x*100:.1f}%")
        display_df["income_score"] = display_df["income_score"].apply(lambda x: f"{x:.2f}")
        print(display_df.to_string(index=False))

    # 6. Quick Greeks calculation demo
    print("\n[6] Direct Greeks calculation example...")
    greeks = calculate_greeks(
        option_type="put",
        underlying_price=chain.underlying_price,
        strike=chain.underlying_price * 0.95,  # 5% OTM
        time_to_expiry=30/365,
        iv=0.35,
    )
    print(f"    {greeks}")

    print(f"\n{'='*60}")
    print("  SECTION 1 COMPLETE - Options Data Layer Working!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

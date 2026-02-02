"""
Options filtering utilities for strike selection.
"""

from dataclasses import dataclass
from typing import Literal, Optional
import pandas as pd

from src.options.greeks import add_greeks_to_chain


@dataclass
class OptimalStrike:
    """Recommended strike with analysis."""
    strike: float
    delta: float
    premium: float          # Mid price
    bid: float
    ask: float
    iv: float
    dte: int
    theta: float            # Daily theta decay
    annual_return: float    # Annualized return if OTM at expiry
    breakeven: float        # Stock price at breakeven
    reason: str             # Why this strike was selected


def filter_by_delta(
    df: pd.DataFrame,
    option_type: Literal["call", "put"],
    min_delta: float = 0.15,
    max_delta: float = 0.35,
    min_premium: float = 0.50,
    min_volume: int = 0,
    max_spread_pct: float = 0.20,
) -> pd.DataFrame:
    """
    Filter options chain by delta range and quality criteria.

    Args:
        df: Options chain DataFrame (calls or puts)
        option_type: "call" or "put" (for Greeks calculation)
        min_delta: Minimum absolute delta (default 0.15)
        max_delta: Maximum absolute delta (default 0.35)
        min_premium: Minimum mid price in dollars (default $0.50)
        min_volume: Minimum volume (default 0)
        max_spread_pct: Maximum bid-ask spread as % of mid (default 20%)

    Returns:
        Filtered DataFrame with Greeks columns added

    Example:
        >>> chain = get_options_chain("NVDA")
        >>> puts = filter_by_delta(chain.puts, "put", min_delta=0.20, max_delta=0.30)
        >>> puts[["strike", "mid_price", "delta", "theta", "iv"]]
    """
    # Add Greeks if not present
    if "delta" not in df.columns:
        df = add_greeks_to_chain(df, option_type)

    # Work with absolute delta for puts (puts have negative delta)
    df = df.copy()
    df["abs_delta"] = df["delta"].abs()

    # Apply filters
    mask = (
        (df["abs_delta"] >= min_delta) &
        (df["abs_delta"] <= max_delta) &
        (df["mid_price"] >= min_premium)
    )

    # Volume filter (if column exists and volume > 0)
    if "volume" in df.columns and min_volume > 0:
        mask &= df["volume"] >= min_volume

    # Spread filter
    if "spread_pct" in df.columns:
        mask &= df["spread_pct"] <= max_spread_pct

    filtered = df[mask].copy()

    # Sort by delta (closest to target range midpoint)
    target_delta = (min_delta + max_delta) / 2
    filtered["delta_distance"] = (filtered["abs_delta"] - target_delta).abs()
    filtered = filtered.sort_values("delta_distance")

    return filtered


def find_optimal_strike(
    df: pd.DataFrame,
    option_type: Literal["call", "put"],
    target_delta: float = 0.25,
    underlying_price: Optional[float] = None,
) -> Optional[OptimalStrike]:
    """
    Find the optimal strike for income generation.

    For puts: Sell OTM puts with target delta (probability of assignment)
    For calls: Sell OTM calls with target delta (probability of being called away)

    Args:
        df: Options chain DataFrame
        option_type: "call" or "put"
        target_delta: Target absolute delta (default 0.25 = ~75% OTM probability)
        underlying_price: Current stock price (used for return calculations)

    Returns:
        OptimalStrike with full analysis, or None if no suitable strike found

    Example:
        >>> chain = get_options_chain("NVDA")
        >>> optimal = find_optimal_strike(chain.puts, "put", target_delta=0.25)
        >>> print(f"Sell {optimal.strike} put for ${optimal.premium:.2f}")
    """
    # Add Greeks if not present
    if "delta" not in df.columns:
        df = add_greeks_to_chain(df, option_type)

    if df.empty:
        return None

    df = df.copy()
    df["abs_delta"] = df["delta"].abs()

    # Get underlying price
    if underlying_price is None:
        underlying_price = df["underlying_price"].iloc[0]

    # Filter to reasonable options (OTM for income)
    if option_type == "put":
        # OTM puts: strike < underlying
        df = df[df["strike"] < underlying_price]
    else:
        # OTM calls: strike > underlying
        df = df[df["strike"] > underlying_price]

    if df.empty:
        return None

    # Find closest to target delta
    df["delta_distance"] = (df["abs_delta"] - target_delta).abs()
    df = df.sort_values("delta_distance")

    best = df.iloc[0]

    # Calculate metrics
    premium = best["mid_price"]
    strike = best["strike"]
    dte = best["dte"]
    iv = best.get("impliedVolatility", 0.3)
    theta = best.get("theta", 0.0)

    # Annualized return calculation
    if option_type == "put":
        # Cash-secured put: return = premium / (strike * 100) * (365 / dte)
        capital_required = strike * 100  # Per contract
        annual_return = (premium / strike) * (365 / dte) if dte > 0 else 0
        breakeven = strike - premium
    else:
        # Covered call: return = premium / underlying * (365 / dte)
        capital_required = underlying_price * 100
        annual_return = (premium / underlying_price) * (365 / dte) if dte > 0 else 0
        breakeven = underlying_price + premium

    # Determine reason
    delta_pct = best["abs_delta"] * 100
    if delta_pct < 20:
        reason = f"Conservative: {delta_pct:.0f}% probability of assignment"
    elif delta_pct < 30:
        reason = f"Balanced: {delta_pct:.0f}% assignment probability, good premium"
    else:
        reason = f"Aggressive: {delta_pct:.0f}% assignment probability, higher premium"

    return OptimalStrike(
        strike=strike,
        delta=best["delta"],
        premium=premium,
        bid=best["bid"],
        ask=best["ask"],
        iv=iv if not pd.isna(iv) else 0.3,
        dte=dte,
        theta=theta,
        annual_return=annual_return,
        breakeven=breakeven,
        reason=reason,
    )


def rank_strikes_for_income(
    df: pd.DataFrame,
    option_type: Literal["call", "put"],
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Rank strikes by income potential (risk-adjusted).

    Returns top N strikes sorted by a composite score considering:
    - Premium yield (higher is better)
    - Delta (lower is safer)
    - Theta decay (higher is better for sellers)
    - Bid-ask spread (lower is better)

    Args:
        df: Options chain DataFrame
        option_type: "call" or "put"
        top_n: Number of top strikes to return

    Returns:
        DataFrame with top strikes and income_score column
    """
    if "delta" not in df.columns:
        df = add_greeks_to_chain(df, option_type)

    df = df.copy()
    underlying = df["underlying_price"].iloc[0]

    # Filter to OTM options
    if option_type == "put":
        df = df[df["strike"] < underlying]
    else:
        df = df[df["strike"] > underlying]

    if df.empty:
        return df

    df["abs_delta"] = df["delta"].abs()

    # Calculate yield (annualized)
    dte = df["dte"].iloc[0]
    if option_type == "put":
        df["yield"] = (df["mid_price"] / df["strike"]) * (365 / dte) if dte > 0 else 0
    else:
        df["yield"] = (df["mid_price"] / underlying) * (365 / dte) if dte > 0 else 0

    # Composite score: higher yield, lower delta (safer), tighter spread
    # Normalize components to 0-1 range
    df["yield_score"] = df["yield"] / df["yield"].max() if df["yield"].max() > 0 else 0
    df["delta_score"] = 1 - (df["abs_delta"] / df["abs_delta"].max()) if df["abs_delta"].max() > 0 else 0
    df["spread_score"] = 1 - (df["spread_pct"] / df["spread_pct"].max()) if "spread_pct" in df.columns and df["spread_pct"].max() > 0 else 0.5

    # Weighted composite (yield most important for income)
    df["income_score"] = (
        df["yield_score"] * 0.5 +
        df["delta_score"] * 0.3 +
        df["spread_score"] * 0.2
    )

    # Sort and return top N
    result = df.sort_values("income_score", ascending=False).head(top_n)

    return result[[
        "strike", "bid", "ask", "mid_price", "delta", "theta",
        "impliedVolatility", "dte", "yield", "income_score"
    ]]

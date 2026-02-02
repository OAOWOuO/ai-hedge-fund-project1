"""
Options chain data fetching via yfinance.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
import pandas as pd
import yfinance as yf


@dataclass
class OptionsChain:
    """Container for options chain data."""
    ticker: str
    underlying_price: float
    expiration: date
    calls: pd.DataFrame
    puts: pd.DataFrame
    fetched_at: datetime

    def __repr__(self) -> str:
        return f"OptionsChain({self.ticker}, exp={self.expiration}, calls={len(self.calls)}, puts={len(self.puts)})"


def get_options_chain(
    ticker: str,
    expiration: Optional[str] = None,
    min_dte: int = 20,
    max_dte: int = 60,
) -> OptionsChain:
    """
    Fetch options chain for a ticker.

    Args:
        ticker: Stock symbol (e.g., "NVDA")
        expiration: Specific expiration date (YYYY-MM-DD). If None, picks based on DTE range.
        min_dte: Minimum days to expiration (default 20)
        max_dte: Maximum days to expiration (default 60)

    Returns:
        OptionsChain with calls and puts DataFrames

    Example:
        >>> chain = get_options_chain("NVDA")
        >>> chain.puts[["strike", "bid", "ask", "impliedVolatility"]]
    """
    stock = yf.Ticker(ticker)

    # Get underlying price
    underlying_price = stock.info.get("regularMarketPrice") or stock.info.get("currentPrice")
    if underlying_price is None:
        hist = stock.history(period="1d")
        underlying_price = hist["Close"].iloc[-1] if not hist.empty else 0.0

    # Get available expirations
    expirations = stock.options
    if not expirations:
        raise ValueError(f"No options available for {ticker}")

    # Select expiration
    if expiration:
        if expiration not in expirations:
            raise ValueError(f"Expiration {expiration} not available. Available: {expirations[:5]}...")
        selected_exp = expiration
    else:
        # Find expiration in DTE range
        today = date.today()
        selected_exp = None
        for exp in expirations:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            dte = (exp_date - today).days
            if min_dte <= dte <= max_dte:
                selected_exp = exp
                break

        if selected_exp is None:
            # Fall back to first available if none in range
            selected_exp = expirations[0]

    # Fetch option chain
    opt = stock.option_chain(selected_exp)

    # Add useful columns
    exp_date = datetime.strptime(selected_exp, "%Y-%m-%d").date()
    dte = (exp_date - date.today()).days

    calls = opt.calls.copy()
    puts = opt.puts.copy()

    # Add computed columns
    for df in [calls, puts]:
        df["dte"] = dte
        df["underlying_price"] = underlying_price
        df["mid_price"] = (df["bid"] + df["ask"]) / 2
        df["spread"] = df["ask"] - df["bid"]
        df["spread_pct"] = df["spread"] / df["mid_price"].replace(0, float("nan"))
        df["moneyness"] = df["strike"] / underlying_price

    return OptionsChain(
        ticker=ticker,
        underlying_price=underlying_price,
        expiration=exp_date,
        calls=calls,
        puts=puts,
        fetched_at=datetime.now(),
    )


def get_expirations(ticker: str) -> list[str]:
    """Get all available expiration dates for a ticker."""
    stock = yf.Ticker(ticker)
    return list(stock.options)


def get_underlying_price(ticker: str) -> float:
    """Get current underlying stock price."""
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice") or stock.info.get("currentPrice")
    if price is None:
        hist = stock.history(period="1d")
        price = hist["Close"].iloc[-1] if not hist.empty else 0.0
    return float(price)

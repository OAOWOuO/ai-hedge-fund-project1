"""
Greeks calculation using py_vollib (Black-Scholes-Merton model).
"""

from dataclasses import dataclass
from typing import Literal
import pandas as pd
import numpy as np

from py_vollib.black_scholes_merton import black_scholes_merton as bsm
from py_vollib.black_scholes_merton.greeks.analytical import delta as bsm_delta
from py_vollib.black_scholes_merton.greeks.analytical import gamma as bsm_gamma
from py_vollib.black_scholes_merton.greeks.analytical import theta as bsm_theta
from py_vollib.black_scholes_merton.greeks.analytical import vega as bsm_vega
from py_vollib.black_scholes_merton.greeks.analytical import rho as bsm_rho


# Risk-free rate (approximate, should be fetched from treasury yields)
RISK_FREE_RATE = 0.05  # 5%
DIVIDEND_YIELD = 0.0   # Assume 0 for simplicity


@dataclass
class Greeks:
    """Container for option Greeks."""
    delta: float      # Price sensitivity to underlying
    gamma: float      # Delta sensitivity to underlying
    theta: float      # Time decay (daily)
    vega: float       # IV sensitivity
    rho: float        # Interest rate sensitivity
    iv: float         # Implied volatility used

    def __repr__(self) -> str:
        return f"Greeks(Δ={self.delta:.3f}, Γ={self.gamma:.4f}, Θ={self.theta:.3f}, V={self.vega:.3f})"


def calculate_greeks(
    option_type: Literal["call", "put"],
    underlying_price: float,
    strike: float,
    time_to_expiry: float,  # In years (e.g., 30 days = 30/365)
    iv: float,              # Implied volatility as decimal (e.g., 0.35 for 35%)
    risk_free_rate: float = RISK_FREE_RATE,
    dividend_yield: float = DIVIDEND_YIELD,
) -> Greeks:
    """
    Calculate option Greeks using Black-Scholes-Merton model.

    Args:
        option_type: "call" or "put"
        underlying_price: Current stock price
        strike: Option strike price
        time_to_expiry: Time to expiration in years
        iv: Implied volatility as decimal
        risk_free_rate: Risk-free interest rate
        dividend_yield: Continuous dividend yield

    Returns:
        Greeks dataclass with delta, gamma, theta, vega, rho

    Example:
        >>> greeks = calculate_greeks("put", 140.0, 130.0, 30/365, 0.35)
        >>> print(f"Delta: {greeks.delta:.3f}")
    """
    flag = "c" if option_type == "call" else "p"

    # Handle edge cases
    if time_to_expiry <= 0:
        time_to_expiry = 1 / 365  # Minimum 1 day
    if iv <= 0:
        iv = 0.01  # Minimum 1% IV

    try:
        delta = bsm_delta(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)
        gamma = bsm_gamma(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)
        theta = bsm_theta(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)
        vega = bsm_vega(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)
        rho = bsm_rho(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)

        # Convert theta to daily (vollib returns annualized)
        theta_daily = theta / 365

        return Greeks(
            delta=delta,
            gamma=gamma,
            theta=theta_daily,
            vega=vega / 100,  # Convert to per 1% IV change
            rho=rho,
            iv=iv,
        )
    except Exception as e:
        # Return zero Greeks on calculation error
        return Greeks(delta=0.0, gamma=0.0, theta=0.0, vega=0.0, rho=0.0, iv=iv)


def add_greeks_to_chain(df: pd.DataFrame, option_type: Literal["call", "put"]) -> pd.DataFrame:
    """
    Add Greeks columns to an options chain DataFrame.

    Expects DataFrame with columns: strike, underlying_price, dte, impliedVolatility

    Returns DataFrame with additional columns: delta, gamma, theta, vega
    """
    df = df.copy()

    greeks_data = []
    for _, row in df.iterrows():
        tte = row["dte"] / 365  # Convert DTE to years
        iv = row.get("impliedVolatility", 0.3)  # Default to 30% if missing

        if pd.isna(iv) or iv <= 0:
            iv = 0.3

        greeks = calculate_greeks(
            option_type=option_type,
            underlying_price=row["underlying_price"],
            strike=row["strike"],
            time_to_expiry=tte,
            iv=iv,
        )
        greeks_data.append({
            "delta": greeks.delta,
            "gamma": greeks.gamma,
            "theta": greeks.theta,
            "vega": greeks.vega,
        })

    greeks_df = pd.DataFrame(greeks_data)
    for col in greeks_df.columns:
        df[col] = greeks_df[col].values

    return df


def calculate_theoretical_price(
    option_type: Literal["call", "put"],
    underlying_price: float,
    strike: float,
    time_to_expiry: float,
    iv: float,
    risk_free_rate: float = RISK_FREE_RATE,
    dividend_yield: float = DIVIDEND_YIELD,
) -> float:
    """Calculate theoretical option price using BSM model."""
    flag = "c" if option_type == "call" else "p"

    if time_to_expiry <= 0:
        time_to_expiry = 1 / 365
    if iv <= 0:
        iv = 0.01

    try:
        return bsm(flag, underlying_price, strike, time_to_expiry, risk_free_rate, iv, dividend_yield)
    except Exception:
        return 0.0

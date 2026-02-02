"""
Options module for AI-Powered Options Wheel System.

Provides:
- Options chain data fetching (yfinance)
- Greeks calculation (vollib)
- Delta-based filtering for strike selection
- AI → Options bridge (agent signals to trade opportunities)
"""

from src.options.data import get_options_chain, OptionsChain
from src.options.greeks import calculate_greeks, Greeks
from src.options.filters import filter_by_delta, find_optimal_strike
from src.options.bridge import (
    generate_options_opportunities,
    OptionsOpportunity,
    AgentSignal,
    opportunities_to_dataframe,
)

__all__ = [
    # Section 1: Data Layer
    "get_options_chain",
    "OptionsChain",
    "calculate_greeks",
    "Greeks",
    "filter_by_delta",
    "find_optimal_strike",
    # Section 2: AI Bridge
    "generate_options_opportunities",
    "OptionsOpportunity",
    "AgentSignal",
    "opportunities_to_dataframe",
]

# AI-Powered Options Wheel System

## The Problem

Buying stocks outright means:
- Full capital at risk immediately
- No income while waiting for appreciation
- Binary outcome (stock goes up or down)

Options income strategies (covered calls, cash-secured puts) solve this but require:
- Knowing *which* stocks to trade options on
- Strike selection expertise (Greeks, delta targeting)
- Consistent execution discipline

**The gap:** No system combines AI-driven stock selection with systematic options income generation.

## Success Looks Like

1. **AI agents pick stocks** → High-conviction bullish signals
2. **Sell cash-secured puts** → Collect 1-3% monthly premium on picks
3. **If assigned** → Sell covered calls on position
4. **Wheel continues** → Systematic income generation

**Measurable outcomes:**
- Backtest shows positive risk-adjusted returns (Sharpe > 1.0)
- Monthly premium income on deployed capital
- Lower effective cost basis than buy-and-hold
- Clear dashboard showing positions, Greeks, P&L

## Building On (Existing Foundations)

### From ai-hedge-fund repo:
- **17 AI agents** — Stock analysis with confidence scores
- **LangGraph workflow** — Multi-agent orchestration
- **Financial data API** — Price, fundamentals, news, insider trades

### External libraries:
- **vollib** — Greeks calculation (delta, theta, gamma, vega)
- **yfinance + yoptions** — Free options chain data
- **optionlab** — Strategy evaluation and P&L profiles
- **Alpaca API** — Commission-free options trading (paper + live)

### Strategy references:
- **Wheel strategy** — Cash-secured puts → covered calls cycle
- **Delta targeting** — 0.20-0.30 for puts, 0.30-0.40 for calls
- **ThetaGang patterns** — Rolling logic, position management

## The Unique Part

What we're building that doesn't exist:

1. **AI → Options Bridge**
   - Convert agent BUY signals into put-selling opportunities
   - Confidence score maps to position sizing
   - Multi-agent consensus for higher conviction

2. **Greeks-Optimized Strike Selection**
   - Auto-select strikes based on delta targets
   - Account for IV percentile (high IV = better premium)
   - Days-to-expiration optimization (30-45 DTE sweet spot)

3. **Wheel State Machine**
   - Track position lifecycle: CASH → PUT_SOLD → ASSIGNED → CALL_SOLD → CALLED_AWAY
   - Auto-suggest rolls when approaching expiration
   - Calculate breakeven, max profit, probability of profit

4. **Income Dashboard**
   - Premium collected vs. capital deployed
   - Annualized yield by position
   - Greeks exposure across portfolio
   - Upcoming expirations and roll opportunities

## Tech Stack

- **UI:** Streamlit (rapid iteration, show-don't-tell)
- **Backend:** Existing ai-hedge-fund FastAPI (extend)
- **Options Analytics:** vollib, optionlab
- **Options Data:** yfinance + yoptions (free tier), Alpaca (execution)
- **AI Agents:** Existing LangChain/LangGraph agents
- **Calculations:** pandas, numpy

## Open Questions

1. **Paper vs. Live:** Start with Alpaca paper trading? Or backtest-only first?
2. **Agent subset:** Use all 17 agents or focus on value investors (Buffett, Munger, Graham)?
3. **Position sizing:** Fixed dollar amount per trade or Kelly criterion?
4. **Rolling rules:** Auto-roll at 50% profit? Or time-based (7 DTE)?

---

*DRIVER Framework | Cognition Mate (认知伙伴)*
*"Use AI to pick what to trade. Use options to optimize how to enter."*

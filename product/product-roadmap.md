# Product Roadmap: AI-Powered Options Wheel System

## Overview

5 buildable sections, each independently demoable. Build in order — each section unlocks the next.

---

## Section 1: Options Data Layer

**Goal:** Get options chains and calculate Greeks for any ticker.

**Delivers:**
- Fetch options chains (strikes, expirations, bid/ask, IV)
- Calculate Greeks (delta, theta, gamma, vega) via vollib
- Filter chains by delta target (e.g., "show me 0.25-0.30 delta puts")
- Cache to avoid API rate limits

**Demo:**
```python
chain = get_options_chain("NVDA")
puts = filter_by_delta(chain.puts, min_delta=0.20, max_delta=0.30)
# Returns: strike, premium, delta, theta, IV, DTE
```

**Tech:** yfinance, yoptions, vollib, pandas

**Estimate:** Foundation layer — build first

---

## Section 2: AI → Options Bridge

**Goal:** Convert AI agent signals into options trade opportunities.

**Delivers:**
- Run existing agents on ticker list
- Extract BUY signals with confidence > threshold
- Map confidence to position sizing suggestion
- Output: "Sell NVDA $130 put, 30 DTE, Δ0.25, $4.50 premium"

**Demo:**
```python
signals = run_agents(["NVDA", "AAPL", "MSFT"])
opportunities = generate_put_opportunities(signals, delta_target=0.25)
# Returns: ticker, signal, confidence, suggested_strike, premium, greeks
```

**Tech:** Existing LangGraph agents + Section 1

**Depends on:** Section 1

---

## Section 3: Wheel State Machine

**Goal:** Track position lifecycle and suggest actions.

**Delivers:**
- Position states: WATCHING → PUT_SOLD → ASSIGNED → CALL_SOLD → CALLED_AWAY
- Track: entry date, strike, premium collected, current P&L
- Roll triggers: 50% profit OR 7 DTE (whichever first)
- Suggest action: "Roll NVDA put from $130 to $125, collect $2.00 more"

**Demo:**
```python
position = Position("NVDA", state=PUT_SOLD, strike=130, premium=4.50)
position.update(current_price=128, dte=5)
# Returns: "ROLL SUGGESTED - 7 DTE trigger, current profit 40%"
```

**Tech:** Pydantic models, state machine pattern

**Depends on:** Section 1, 2

---

## Section 4: Paper Trading Integration

**Goal:** Execute trades on Alpaca paper account.

**Delivers:**
- Connect to Alpaca paper trading API
- Submit option orders (sell-to-open puts, sell-to-open calls)
- Monitor fills and update positions
- Handle assignment notifications
- Execute rolls (close + open new position)

**Demo:**
```python
alpaca = AlpacaOptionsClient(paper=True)
order = alpaca.sell_put("NVDA", strike=130, expiry="2026-02-28", quantity=1)
# Returns: order_id, status, fill_price
```

**Tech:** alpaca-py SDK, asyncio for monitoring

**Depends on:** Section 3

---

## Section 5: Income Dashboard

**Goal:** Streamlit UI showing everything.

**Delivers:**
- **Opportunities tab:** AI picks + suggested options trades
- **Positions tab:** Current positions, Greeks, P&L, roll suggestions
- **Income tab:** Premium collected, annualized yield, performance chart
- **Execution tab:** One-click trade execution (paper)

**Demo:**
```
streamlit run app/options_dashboard.py
```

Visual dashboard with:
- Table of AI signals → options opportunities
- Position cards with Greeks gauges
- Income chart (cumulative premium over time)
- "Execute" buttons connected to Alpaca paper

**Tech:** Streamlit, plotly, Section 1-4

**Depends on:** All previous sections

---

## Build Order

```
Section 1 ──► Section 2 ──► Section 3 ──► Section 4 ──► Section 5
 (Data)      (AI Bridge)    (State)      (Execute)     (Dashboard)
   │              │            │             │              │
   ▼              ▼            ▼             ▼              ▼
 "I can get    "AI picks    "I know      "Trades       "See it
  Greeks"      generate     what to do    actually      all work
               trades"      next"         happen"       together"
```

---

## Success Metrics

| Section | "Done" When... |
|---------|----------------|
| 1 | Can fetch NVDA options chain with accurate Greeks |
| 2 | Agent BUY signal outputs a specific put to sell |
| 3 | Position tracks from PUT_SOLD through CALLED_AWAY |
| 4 | Paper trade executes and fills on Alpaca |
| 5 | Dashboard shows live positions with P&L |

---

## Open Items

- [ ] Alpaca paper account setup (need API keys)
- [ ] Decide on initial capital allocation ($10k? $50k? $100k paper?)
- [ ] Pick first 3-5 tickers to test with

---

*"Show don't tell — each section produces visible output."*

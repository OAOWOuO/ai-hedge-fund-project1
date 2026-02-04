"""
Stock Analyzer - Technical & Fundamental Analysis
Deep-dive analysis of individual stocks with AI recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="Stock Analyzer | AI Financial Advisor",
    page_icon="📈",
    layout="wide"
)

# ============== CSS ==============
st.markdown("""
<style>
    .main { background: #0d1117; }
    .stApp { background: #0d1117; }
    #MainMenu, footer, header { visibility: hidden; }
    h1, h2, h3, h4 { color: #e6edf3 !important; }
    p, span, label, div { color: #c9d1d9 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #161b22; padding: 8px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; }
    .stTabs [aria-selected="true"] { background: #238636 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ============== DATA FUNCTIONS ==============
@st.cache_data(ttl=300)
def fetch_stock_data(ticker: str) -> dict:
    """Fetch comprehensive stock data."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        if hist.empty:
            return {"valid": False, "ticker": ticker}
        return {
            "valid": True, "ticker": ticker, "info": info, "history": hist,
            "name": info.get("shortName", ticker),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice") or float(hist['Close'].iloc[-1]),
            "change": info.get("regularMarketChange", 0),
            "change_pct": info.get("regularMarketChangePercent", 0),
            "market_cap": info.get("marketCap", 0),
            "volume": info.get("volume", 0),
            "high_52w": info.get("fiftyTwoWeekHigh", 0),
            "low_52w": info.get("fiftyTwoWeekLow", 0),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "ps_ratio": info.get("priceToSalesTrailing12Months"),
            "dividend_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 1),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "profit_margin": info.get("profitMargins"),
            "roe": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "free_cash_flow": info.get("freeCashflow"),
            "target_price": info.get("targetMeanPrice"),
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "analyst_rating": info.get("recommendationKey"),
            "num_analysts": info.get("numberOfAnalystOpinions", 0),
        }
    except:
        return {"valid": False, "ticker": ticker}


def calc_technicals(hist):
    """Calculate technical indicators."""
    df = hist.copy()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['MA200'] = df['Close'].rolling(200).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain / loss))
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df


def get_recommendation(data, tech_df):
    """Generate recommendation based on indicators."""
    score, signals, max_score = 0, [], 0
    if len(tech_df) > 50:
        latest = tech_df.iloc[-1]
        # RSI
        max_score += 2
        if latest['RSI'] < 30:
            score += 2
            signals.append(("RSI Oversold", "bullish", f"RSI at {latest['RSI']:.0f} - potential bounce"))
        elif latest['RSI'] > 70:
            score -= 2
            signals.append(("RSI Overbought", "bearish", f"RSI at {latest['RSI']:.0f} - potential pullback"))
        else:
            signals.append(("RSI Neutral", "neutral", f"RSI at {latest['RSI']:.0f}"))
        # MACD
        max_score += 2
        if latest['MACD'] > latest['MACD_Signal']:
            score += 1
            signals.append(("MACD Bullish", "bullish", "MACD above signal line"))
        else:
            score -= 1
            signals.append(("MACD Bearish", "bearish", "MACD below signal line"))
        # MA
        max_score += 2
        if pd.notna(latest['MA50']) and pd.notna(latest['MA200']):
            if latest['MA50'] > latest['MA200']:
                score += 1
                signals.append(("Golden Cross", "bullish", "50-day MA above 200-day MA"))
            else:
                score -= 1
                signals.append(("Death Cross", "bearish", "50-day MA below 200-day MA"))
    # Fundamentals
    pe = data.get('pe_ratio')
    if pe:
        max_score += 2
        if pe < 15:
            score += 2
            signals.append(("Low P/E", "bullish", f"P/E of {pe:.1f} suggests undervaluation"))
        elif pe > 35:
            score -= 2
            signals.append(("High P/E", "bearish", f"P/E of {pe:.1f} suggests overvaluation"))
    target = data.get('target_price')
    price = data.get('price')
    if target and price:
        max_score += 2
        upside = (target - price) / price * 100
        if upside > 15:
            score += 2
            signals.append(("Strong Upside", "bullish", f"Target implies {upside:.0f}% upside"))
        elif upside < -10:
            score -= 2
            signals.append(("Downside Risk", "bearish", f"Target implies {upside:.0f}% downside"))
    score_pct = (score / max_score * 100) if max_score > 0 else 0
    if score_pct >= 30:
        rec = ("BUY", "#3fb950", "Strong indicators suggest buying opportunity.")
    elif score_pct >= -20:
        rec = ("HOLD", "#d29922", "Mixed signals. Wait for clearer direction.")
    else:
        rec = ("SELL", "#f85149", "Warning signs. Consider reducing exposure.")
    return {"rec": rec[0], "color": rec[1], "text": rec[2], "score": score, "max": max_score, "pct": score_pct, "signals": signals}


# ============== HEADER ==============
st.write("# 📈 Stock Analyzer")
st.caption("Technical & Fundamental Analysis with AI Recommendations")

# ============== MAIN LAYOUT ==============
col_input, col_analysis = st.columns([1, 3])

with col_input:
    st.subheader("Stock Selection")
    ticker = st.text_input("Enter Ticker", value="AAPL", help="e.g., AAPL, MSFT, GOOGL")
    ticker = ticker.strip().upper()
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = None

    if analyze_btn and ticker:
        with st.spinner(f"Analyzing {ticker}..."):
            st.session_state.stock_data = fetch_stock_data(ticker)

    if st.session_state.stock_data and st.session_state.stock_data.get("valid"):
        d = st.session_state.stock_data
        st.divider()
        st.write(f"### {d['name']}")
        st.caption(f"{d['sector']} • {d['industry']}")
        st.metric("Price", f"${d['price']:.2f}", delta=f"{d['change_pct']:.2f}%")
        st.write(f"**Market Cap:** ${d['market_cap']/1e9:.1f}B")
        st.write(f"**Volume:** {d['volume']:,.0f}")
        st.write(f"**52W Range:** ${d['low_52w']:.0f} - ${d['high_52w']:.0f}")
        if d['high_52w'] > d['low_52w']:
            pos = (d['price'] - d['low_52w']) / (d['high_52w'] - d['low_52w'])
            st.progress(min(1, max(0, pos)), text=f"52W Position: {pos*100:.0f}%")

with col_analysis:
    if st.session_state.stock_data and st.session_state.stock_data.get("valid"):
        d = st.session_state.stock_data
        hist = d.get("history")
        if hist is not None and not hist.empty:
            tech_df = calc_technicals(hist)
            rec = get_recommendation(d, tech_df)

            # Recommendation box
            st.markdown(f"""
            <div style="background:#161b22; border-left:4px solid {rec['color']}; padding:20px; border-radius:8px; margin-bottom:20px;">
                <span style="font-size:28px; font-weight:700; color:{rec['color']};">{rec['rec']}</span>
                <span style="color:#8b949e; margin-left:15px;">Score: {rec['score']}/{rec['max']} ({rec['pct']:.0f}%)</span>
                <p style="margin-top:10px; color:#c9d1d9;">{rec['text']}</p>
            </div>
            """, unsafe_allow_html=True)

            tab_tech, tab_fund = st.tabs(["📊 Technical Analysis", "📋 Fundamental Analysis"])

            with tab_tech:
                st.write("### Price & Moving Averages")
                chart_data = tech_df.reset_index()
                chart_data['Date'] = pd.to_datetime(chart_data['Date']).dt.tz_localize(None)

                price_chart = alt.Chart(chart_data).mark_line(color='#58a6ff', strokeWidth=2).encode(
                    x=alt.X('Date:T', title=None, axis=alt.Axis(labelColor='#8b949e')),
                    y=alt.Y('Close:Q', title='Price ($)', axis=alt.Axis(labelColor='#8b949e')),
                    tooltip=[alt.Tooltip('Date:T', format='%Y-%m-%d'), alt.Tooltip('Close:Q', format='$.2f')]
                )
                ma50 = alt.Chart(chart_data).mark_line(color='#f0883e', strokeWidth=1, strokeDash=[5,5]).encode(x='Date:T', y='MA50:Q')
                ma200 = alt.Chart(chart_data).mark_line(color='#a371f7', strokeWidth=1, strokeDash=[5,5]).encode(x='Date:T', y='MA200:Q')
                st.altair_chart((price_chart + ma50 + ma200).properties(height=300).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                st.caption("🔵 Price  🟠 50-day MA  🟣 200-day MA")

                st.write("### Volume")
                vol_chart = alt.Chart(chart_data).mark_bar(color='#58a6ff', opacity=0.6).encode(
                    x=alt.X('Date:T', title=None, axis=alt.Axis(labelColor='#8b949e')),
                    y=alt.Y('Volume:Q', title='Volume', axis=alt.Axis(labelColor='#8b949e'))
                ).properties(height=120).configure_view(strokeWidth=0).configure(background='#161b22')
                st.altair_chart(vol_chart, use_container_width=True)

                col_rsi, col_macd = st.columns(2)
                with col_rsi:
                    st.write("### RSI (14)")
                    rsi_val = tech_df['RSI'].iloc[-1]
                    rsi_chart = alt.Chart(chart_data.tail(100)).mark_line(color='#58a6ff').encode(
                        x=alt.X('Date:T', title=None, axis=alt.Axis(labelColor='#8b949e')),
                        y=alt.Y('RSI:Q', scale=alt.Scale(domain=[0,100]), axis=alt.Axis(labelColor='#8b949e'))
                    )
                    rules = alt.Chart(pd.DataFrame({'y': [30, 70]})).mark_rule(strokeDash=[3,3], color='#6e7681').encode(y='y:Q')
                    st.altair_chart((rsi_chart + rules).properties(height=180).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                    if rsi_val > 70: st.warning(f"RSI {rsi_val:.0f} - Overbought")
                    elif rsi_val < 30: st.success(f"RSI {rsi_val:.0f} - Oversold")
                    else: st.info(f"RSI {rsi_val:.0f} - Neutral")

                with col_macd:
                    st.write("### MACD")
                    macd_chart = alt.Chart(chart_data.tail(100)).mark_line(color='#58a6ff').encode(
                        x=alt.X('Date:T', title=None, axis=alt.Axis(labelColor='#8b949e')),
                        y=alt.Y('MACD:Q', axis=alt.Axis(labelColor='#8b949e'))
                    )
                    sig_chart = alt.Chart(chart_data.tail(100)).mark_line(color='#f0883e').encode(x='Date:T', y='MACD_Signal:Q')
                    hist_chart = alt.Chart(chart_data.tail(100)).mark_bar(opacity=0.5).encode(
                        x='Date:T', y='MACD_Hist:Q',
                        color=alt.condition(alt.datum.MACD_Hist > 0, alt.value('#3fb950'), alt.value('#f85149'))
                    )
                    st.altair_chart((hist_chart + macd_chart + sig_chart).properties(height=180).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                    if tech_df['MACD'].iloc[-1] > tech_df['MACD_Signal'].iloc[-1]: st.success("MACD above signal - Bullish")
                    else: st.warning("MACD below signal - Bearish")

                st.write("### Technical Signals")
                for name, sentiment, desc in rec['signals']:
                    if sentiment == 'bullish': st.success(f"**{name}**: {desc}")
                    elif sentiment == 'bearish': st.error(f"**{name}**: {desc}")
                    else: st.info(f"**{name}**: {desc}")

            with tab_fund:
                st.write("### Valuation Metrics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("P/E Ratio", f"{d.get('pe_ratio'):.1f}" if d.get('pe_ratio') else "N/A")
                c2.metric("Forward P/E", f"{d.get('forward_pe'):.1f}" if d.get('forward_pe') else "N/A")
                c3.metric("P/B Ratio", f"{d.get('pb_ratio'):.1f}" if d.get('pb_ratio') else "N/A")
                c4.metric("P/S Ratio", f"{d.get('ps_ratio'):.1f}" if d.get('ps_ratio') else "N/A")

                st.divider()
                st.write("### Growth & Profitability")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Revenue Growth", f"{d.get('revenue_growth')*100:.1f}%" if d.get('revenue_growth') else "N/A")
                c2.metric("Earnings Growth", f"{d.get('earnings_growth')*100:.1f}%" if d.get('earnings_growth') else "N/A")
                c3.metric("Profit Margin", f"{d.get('profit_margin')*100:.1f}%" if d.get('profit_margin') else "N/A")
                c4.metric("ROE", f"{d.get('roe')*100:.1f}%" if d.get('roe') else "N/A")

                st.divider()
                st.write("### Financial Health")
                c1, c2, c3 = st.columns(3)
                c1.metric("Debt/Equity", f"{d.get('debt_to_equity'):.1f}" if d.get('debt_to_equity') else "N/A")
                c2.metric("Current Ratio", f"{d.get('current_ratio'):.1f}" if d.get('current_ratio') else "N/A")
                c3.metric("Free Cash Flow", f"${d.get('free_cash_flow')/1e9:.1f}B" if d.get('free_cash_flow') else "N/A")

                st.divider()
                st.write("### Analyst Price Targets")
                if d.get('target_price'):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Target Low", f"${d.get('target_low'):.0f}" if d.get('target_low') else "N/A")
                    c2.metric("Target Mean", f"${d.get('target_price'):.0f}")
                    c3.metric("Target High", f"${d.get('target_high'):.0f}" if d.get('target_high') else "N/A")
                    upside = (d['target_price'] - d['price']) / d['price'] * 100
                    c4.metric("Implied Upside", f"{upside:+.1f}%")
                    st.caption(f"Based on {d.get('num_analysts', 0)} analyst estimates")
                else:
                    st.info("No analyst targets available for this stock.")
    else:
        st.info("👈 Enter a stock ticker and click **Analyze** to see technical and fundamental analysis with AI recommendations.")

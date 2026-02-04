"""
AI Financial Advisor
Combined app with session state navigation
"""

import streamlit as st

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'

# CSS
st.markdown("""
<style>
    .main { background: #0d1117; }
    .stApp { background: #0d1117; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebarNav"] { display: none; }
    h1, h2, h3, h4 { color: #e6edf3 !important; font-weight: 600 !important; }
    p, span, label, li, div { color: #c9d1d9 !important; }
    .stButton > button {
        background: #238636 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        font-size: 16px !important;
        width: 100%;
    }
    .stButton > button:hover { background: #2ea043 !important; }
    .back-btn button {
        background: #21262d !important;
        border: 1px solid #30363d !important;
    }
    .tool-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
    }
    .tool-card:hover { border-color: #58a6ff; }
</style>
""", unsafe_allow_html=True)


# ============== HOME VIEW ==============
def show_home():
    st.markdown("""
    <div style="text-align: center; padding: 40px 0 30px 0;">
        <h1 style="font-size: 42px;">🏦 AI Financial Advisor</h1>
        <p style="font-size: 18px; color: #8b949e;">Your intelligent assistant for smarter investment decisions</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="tool-card">
            <div style="font-size: 48px; margin-bottom: 15px;">📊</div>
            <div style="font-size: 24px; font-weight: 600; color: #e6edf3 !important;">Portfolio Allocator</div>
            <p style="color: #8b949e; margin: 15px 0;">
                Optimize your multi-stock portfolio with AI-powered allocation,
                risk analytics, and rebalancing recommendations.
            </p>
            <ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
                <li>Multi-stock signal analysis</li>
                <li>Position sizing & allocation</li>
                <li>Risk metrics (Sharpe, Beta, VaR)</li>
                <li>Performance vs S&P 500</li>
                <li>Dividend income tracking</li>
                <li>One-click rebalancing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Portfolio Allocator →", key="btn_portfolio", use_container_width=True):
            st.session_state.current_view = 'portfolio'
            st.rerun()

    with col2:
        st.markdown("""
        <div class="tool-card">
            <div style="font-size: 48px; margin-bottom: 15px;">📈</div>
            <div style="font-size: 24px; font-weight: 600; color: #e6edf3 !important;">Stock Analyzer</div>
            <p style="color: #8b949e; margin: 15px 0;">
                Deep-dive analysis of individual stocks with technical indicators
                and fundamental metrics to find the best opportunities.
            </p>
            <ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
                <li>Price charts with moving averages</li>
                <li>Technical indicators (RSI, MACD)</li>
                <li>Fundamental ratios (P/E, P/B, P/S)</li>
                <li>Growth & profitability metrics</li>
                <li>Analyst price targets</li>
                <li>AI BUY/HOLD/SELL recommendation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Stock Analyzer →", key="btn_analyzer", use_container_width=True):
            st.session_state.current_view = 'analyzer'
            st.rerun()

    st.markdown("""
    <div style="text-align: center; color: #6e7681; font-size: 12px; padding: 40px 20px;">
        Data provided by Yahoo Finance (15-20 min delayed) • For educational purposes only • Not financial advice
    </div>
    """, unsafe_allow_html=True)


# ============== STOCK ANALYZER VIEW ==============
def show_analyzer():
    import pandas as pd
    import numpy as np
    import altair as alt
    from datetime import datetime, timedelta

    # Back button
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Back", key="back_analyzer"):
            st.session_state.current_view = 'home'
            st.rerun()
    with col_title:
        st.write("# 📈 Stock Analyzer")
        st.caption("Technical & Fundamental Analysis with AI Recommendations")

    @st.cache_data(ttl=300)
    def fetch_stock_data(ticker):
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            if hist.empty:
                return {"valid": False}
            return {
                "valid": True, "ticker": ticker, "history": hist,
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "price": info.get("currentPrice") or info.get("regularMarketPrice") or float(hist['Close'].iloc[-1]),
                "change_pct": info.get("regularMarketChangePercent", 0),
                "market_cap": info.get("marketCap", 0),
                "volume": info.get("volume", 0),
                "high_52w": info.get("fiftyTwoWeekHigh", 0),
                "low_52w": info.get("fiftyTwoWeekLow", 0),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
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
                "num_analysts": info.get("numberOfAnalystOpinions", 0),
            }
        except:
            return {"valid": False}

    def calc_technicals(hist):
        df = hist.copy()
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
        score, signals, max_score = 0, [], 0
        if len(tech_df) > 50:
            latest = tech_df.iloc[-1]
            max_score += 2
            if latest['RSI'] < 30:
                score += 2; signals.append(("RSI Oversold", "bullish", f"RSI at {latest['RSI']:.0f}"))
            elif latest['RSI'] > 70:
                score -= 2; signals.append(("RSI Overbought", "bearish", f"RSI at {latest['RSI']:.0f}"))
            else:
                signals.append(("RSI Neutral", "neutral", f"RSI at {latest['RSI']:.0f}"))
            max_score += 2
            if latest['MACD'] > latest['MACD_Signal']:
                score += 1; signals.append(("MACD Bullish", "bullish", "Above signal"))
            else:
                score -= 1; signals.append(("MACD Bearish", "bearish", "Below signal"))
            max_score += 2
            if pd.notna(latest['MA50']) and pd.notna(latest['MA200']):
                if latest['MA50'] > latest['MA200']:
                    score += 1; signals.append(("Golden Cross", "bullish", "MA50 > MA200"))
                else:
                    score -= 1; signals.append(("Death Cross", "bearish", "MA50 < MA200"))
        pe = data.get('pe_ratio')
        if pe:
            max_score += 2
            if pe < 15: score += 2; signals.append(("Low P/E", "bullish", f"P/E {pe:.1f}"))
            elif pe > 35: score -= 2; signals.append(("High P/E", "bearish", f"P/E {pe:.1f}"))
        target, price = data.get('target_price'), data.get('price')
        if target and price:
            max_score += 2
            upside = (target - price) / price * 100
            if upside > 15: score += 2; signals.append(("Strong Upside", "bullish", f"{upside:.0f}% to target"))
            elif upside < -10: score -= 2; signals.append(("Downside Risk", "bearish", f"{upside:.0f}%"))
        score_pct = (score / max_score * 100) if max_score > 0 else 0
        if score_pct >= 30: rec = ("BUY", "#3fb950", "Strong buy signals.")
        elif score_pct >= -20: rec = ("HOLD", "#d29922", "Mixed signals.")
        else: rec = ("SELL", "#f85149", "Warning signs.")
        return {"rec": rec[0], "color": rec[1], "text": rec[2], "score": score, "max": max_score, "pct": score_pct, "signals": signals}

    col_input, col_analysis = st.columns([1, 3])

    with col_input:
        st.subheader("Stock Selection")
        ticker = st.text_input("Enter Ticker", value="AAPL", key="analyzer_ticker")
        ticker = ticker.strip().upper()
        if st.button("🔍 Analyze", type="primary", use_container_width=True, key="analyze_btn"):
            st.session_state.analyzer_data = fetch_stock_data(ticker)

        if 'analyzer_data' not in st.session_state:
            st.session_state.analyzer_data = None

        if st.session_state.analyzer_data and st.session_state.analyzer_data.get("valid"):
            d = st.session_state.analyzer_data
            st.divider()
            st.write(f"### {d['name']}")
            st.caption(f"{d['sector']} • {d['industry']}")
            st.metric("Price", f"${d['price']:.2f}", delta=f"{d['change_pct']:.2f}%")
            st.write(f"**Market Cap:** ${d['market_cap']/1e9:.1f}B")
            st.write(f"**52W Range:** ${d['low_52w']:.0f} - ${d['high_52w']:.0f}")
            if d['high_52w'] > d['low_52w']:
                pos = (d['price'] - d['low_52w']) / (d['high_52w'] - d['low_52w'])
                st.progress(min(1, max(0, pos)), text=f"Position: {pos*100:.0f}%")

    with col_analysis:
        if st.session_state.analyzer_data and st.session_state.analyzer_data.get("valid"):
            d = st.session_state.analyzer_data
            hist = d.get("history")
            if hist is not None and not hist.empty:
                tech_df = calc_technicals(hist)
                rec = get_recommendation(d, tech_df)

                st.markdown(f"""
                <div style="background:#161b22; border-left:4px solid {rec['color']}; padding:20px; border-radius:8px; margin-bottom:20px;">
                    <span style="font-size:28px; font-weight:700; color:{rec['color']};">{rec['rec']}</span>
                    <span style="color:#8b949e; margin-left:15px;">Score: {rec['score']}/{rec['max']} ({rec['pct']:.0f}%)</span>
                    <p style="margin-top:10px; color:#c9d1d9;">{rec['text']}</p>
                </div>
                """, unsafe_allow_html=True)

                tab_tech, tab_fund = st.tabs(["📊 Technical", "📋 Fundamental"])

                with tab_tech:
                    st.write("### Price & Moving Averages")
                    chart_data = tech_df.reset_index()
                    chart_data['Date'] = pd.to_datetime(chart_data['Date']).dt.tz_localize(None)
                    price_chart = alt.Chart(chart_data).mark_line(color='#58a6ff', strokeWidth=2).encode(
                        x=alt.X('Date:T', title=None), y=alt.Y('Close:Q', title='Price'),
                        tooltip=[alt.Tooltip('Date:T', format='%Y-%m-%d'), alt.Tooltip('Close:Q', format='$.2f')]
                    )
                    ma50 = alt.Chart(chart_data).mark_line(color='#f0883e', strokeDash=[5,5]).encode(x='Date:T', y='MA50:Q')
                    ma200 = alt.Chart(chart_data).mark_line(color='#a371f7', strokeDash=[5,5]).encode(x='Date:T', y='MA200:Q')
                    st.altair_chart((price_chart + ma50 + ma200).properties(height=280).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                    st.caption("🔵 Price  🟠 MA50  🟣 MA200")

                    col_rsi, col_macd = st.columns(2)
                    with col_rsi:
                        st.write("### RSI")
                        rsi_val = tech_df['RSI'].iloc[-1]
                        rsi_chart = alt.Chart(chart_data.tail(100)).mark_line(color='#58a6ff').encode(x='Date:T', y=alt.Y('RSI:Q', scale=alt.Scale(domain=[0,100])))
                        rules = alt.Chart(pd.DataFrame({'y': [30, 70]})).mark_rule(strokeDash=[3,3], color='#6e7681').encode(y='y:Q')
                        st.altair_chart((rsi_chart + rules).properties(height=160).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                        if rsi_val > 70: st.warning(f"RSI {rsi_val:.0f} - Overbought")
                        elif rsi_val < 30: st.success(f"RSI {rsi_val:.0f} - Oversold")
                        else: st.info(f"RSI {rsi_val:.0f} - Neutral")

                    with col_macd:
                        st.write("### MACD")
                        macd_c = alt.Chart(chart_data.tail(100)).mark_line(color='#58a6ff').encode(x='Date:T', y='MACD:Q')
                        sig_c = alt.Chart(chart_data.tail(100)).mark_line(color='#f0883e').encode(x='Date:T', y='MACD_Signal:Q')
                        hist_c = alt.Chart(chart_data.tail(100)).mark_bar(opacity=0.5).encode(x='Date:T', y='MACD_Hist:Q', color=alt.condition(alt.datum.MACD_Hist > 0, alt.value('#3fb950'), alt.value('#f85149')))
                        st.altair_chart((hist_c + macd_c + sig_c).properties(height=160).configure_view(strokeWidth=0).configure(background='#161b22'), use_container_width=True)
                        if tech_df['MACD'].iloc[-1] > tech_df['MACD_Signal'].iloc[-1]: st.success("Bullish")
                        else: st.warning("Bearish")

                    st.write("### Signals")
                    for name, sentiment, desc in rec['signals']:
                        if sentiment == 'bullish': st.success(f"**{name}**: {desc}")
                        elif sentiment == 'bearish': st.error(f"**{name}**: {desc}")
                        else: st.info(f"**{name}**: {desc}")

                with tab_fund:
                    st.write("### Valuation")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("P/E", f"{d.get('pe_ratio'):.1f}" if d.get('pe_ratio') else "N/A")
                    c2.metric("Fwd P/E", f"{d.get('forward_pe'):.1f}" if d.get('forward_pe') else "N/A")
                    c3.metric("P/B", f"{d.get('pb_ratio'):.1f}" if d.get('pb_ratio') else "N/A")
                    c4.metric("P/S", f"{d.get('ps_ratio'):.1f}" if d.get('ps_ratio') else "N/A")

                    st.write("### Growth")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Rev Growth", f"{d.get('revenue_growth')*100:.1f}%" if d.get('revenue_growth') else "N/A")
                    c2.metric("Earn Growth", f"{d.get('earnings_growth')*100:.1f}%" if d.get('earnings_growth') else "N/A")
                    c3.metric("Margin", f"{d.get('profit_margin')*100:.1f}%" if d.get('profit_margin') else "N/A")
                    c4.metric("ROE", f"{d.get('roe')*100:.1f}%" if d.get('roe') else "N/A")

                    st.write("### Analyst Targets")
                    if d.get('target_price'):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Low", f"${d.get('target_low'):.0f}" if d.get('target_low') else "N/A")
                        c2.metric("Mean", f"${d.get('target_price'):.0f}")
                        c3.metric("High", f"${d.get('target_high'):.0f}" if d.get('target_high') else "N/A")
                        upside = (d['target_price'] - d['price']) / d['price'] * 100
                        c4.metric("Upside", f"{upside:+.1f}%")
                    else:
                        st.info("No analyst targets available")
        else:
            st.info("👈 Enter a ticker and click **Analyze** to see analysis.")


# ============== MAIN ROUTING ==============
if st.session_state.current_view == 'home':
    show_home()
elif st.session_state.current_view == 'analyzer':
    show_analyzer()
elif st.session_state.current_view == 'portfolio':
    # Back button and then run portfolio allocator
    import os
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Back", key="back_portfolio"):
            st.session_state.current_view = 'home'
            st.rerun()

    # Import and run portfolio allocator
    import importlib.util
    spec = importlib.util.spec_from_file_location("portfolio", os.path.join(os.path.dirname(__file__), "portfolio_allocator.py"))
    portfolio_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(portfolio_module)

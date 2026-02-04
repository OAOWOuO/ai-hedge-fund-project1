"""
AI Financial Advisor - Landing Page
"""

import streamlit as st

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="🏦",
    layout="wide"
)

st.markdown("""
<style>
    .main { background: #0d1117; }
    .stApp { background: #0d1117; }
    #MainMenu, footer, header { visibility: hidden; }
    h1, h2, h3 { color: #e6edf3 !important; }
    p, span, div { color: #c9d1d9 !important; }
    .tool-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 30px;
        height: 100%;
    }
    .tool-card:hover { border-color: #58a6ff; }
    .tool-icon { font-size: 48px; text-align: center; margin-bottom: 15px; }
    .tool-title { font-size: 24px; font-weight: 600; color: #e6edf3 !important; text-align: center; }
    .tool-desc { color: #8b949e !important; text-align: center; margin: 15px 0; }
    .feature-list { color: #8b949e !important; padding-left: 20px; }
    .feature-list li { margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h1 style="font-size: 42px;">🏦 AI Financial Advisor</h1>
    <p style="font-size: 18px; color: #8b949e;">Your intelligent assistant for smarter investment decisions</p>
</div>
""", unsafe_allow_html=True)

# Navigation hint
st.info("👈 **Use the sidebar on the left to navigate between tools.** Click the arrow (>) at the top-left if the sidebar is hidden.")

# Tool cards
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">📊</div>
        <div class="tool-title">Portfolio Allocator</div>
        <div class="tool-desc">Optimize your multi-stock portfolio with AI-powered allocation and risk analytics.</div>
        <ul class="feature-list">
            <li>Multi-stock signal analysis</li>
            <li>Position sizing & allocation</li>
            <li>Risk metrics (Sharpe, Beta, VaR)</li>
            <li>Performance vs S&P 500</li>
            <li>Dividend income & earnings calendar</li>
            <li>One-click rebalancing</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">📈</div>
        <div class="tool-title">Stock Analyzer</div>
        <div class="tool-desc">Deep-dive analysis of individual stocks with technical and fundamental metrics.</div>
        <ul class="feature-list">
            <li>Price charts with moving averages</li>
            <li>Technical indicators (RSI, MACD)</li>
            <li>Fundamental ratios (P/E, P/B, P/S)</li>
            <li>Growth & profitability metrics</li>
            <li>Analyst price targets</li>
            <li>AI BUY/HOLD/SELL recommendation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; color: #6e7681; font-size: 12px; padding: 30px;">
    Data provided by Yahoo Finance (15-20 min delayed) • For educational purposes only • Not financial advice
</div>
""", unsafe_allow_html=True)

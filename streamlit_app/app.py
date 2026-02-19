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

if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

st.markdown("""<style>
.main { background: #0d1117; }
.stApp { background: #0d1117; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none; }
h1, h2, h3, h4 { color: #e6edf3 !important; font-weight: 600 !important; }
p, span, label, li, div { color: #c9d1d9 !important; }

/* ── Product / back buttons ── */
.stButton > button {
    background: #1d4ed8 !important;
    color: #e8f0fe !important;
    border: 1px solid #2563eb !important;
    border-radius: 6px !important;
    padding: 12px 24px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    width: 100%;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    background: #2563eb !important;
    border-color: #60a5fa !important;
    color: #fff !important;
}

.tool-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 30px;
    text-align: center;
}
.tool-card:hover { border-color: #58a6ff; }

/* ═══════════════════════════════════════
   FOOTER
   Layout: st.columns() for main content + st.markdown() for copyright.
   Gap between them closed by setting columns padding-bottom: 2rem and
   applying margin-top: -2rem on the copyright element-container.
   Whatever the Streamlit flex gap is (typically 0.5-1rem), the 2rem
   overlap eats into the columns’ bottom padding (not the content),
   so the copyright always sits flush with no visible seam.
   ═══════════════════════════════════════ */

/* ─ Footer columns block ─ */
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) {
    margin-top: 48px;
    background: #07111f !important;
    border-top: 3px solid;
    border-image: linear-gradient(90deg, #0a1628 0%, #1d4ed8 42%, #3b82f6 58%, #0a1628 100%) 1;
    gap: 0 !important;
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) > [data-testid="column"] {
    padding: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) > [data-testid="column"]:not(:last-child) {
    border-right: 1px solid #0d1f38;
}
/* padding-bottom: 2rem (32px) is the key anchor for the gap-close trick below */
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) > [data-testid="column"] > [data-testid="stVerticalBlock"] {
    padding: 28px 28px 32px !important;
    background: #07111f !important;
    gap: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"] {
    padding-left: 44px !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) > [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] {
    padding-right: 44px !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) [data-testid="element-container"] {
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) .stMarkdownContainer {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stVerticalBlock"]:has(.ft-nav-section) .stButton {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}
/* Reset the global color override so footer text uses its own colors */
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) span,
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) div,
[data-testid="stHorizontalBlock"]:has(.ft-nav-section) p { color: inherit !important; }

/* ─ Copyright strip: margin-top -2rem eats into the columns’ 32px bottom padding,
   guaranteeing flush contact regardless of the Streamlit flex gap value ─ */
[data-testid="element-container"]:has(.ft-copy) {
    margin-top: -2rem !important;
    padding: 0 !important;
    line-height: 0 !important;
}
.ft-copy {
    background: #030c17;
    border-top: 1px solid #0d1f38;
    padding: 10px 44px;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 9.5px;
    color: #253d52 !important;
    letter-spacing: 0.05em;
    line-height: 1.4;
}
.ft-copy-sep { color: #142333 !important; }

/* ─ Footer typography ─ */
.ft-section-label {
    display: block;
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #3b82f6 !important;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #0d1f38;
}
.ft-brand-title {
    display: block;
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #b8cfe8 !important;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #0d1f38;
}
.ft-brand-body {
    display: block;
    font-size: 12px;
    line-height: 1.75;
    color: #4e7a9a !important;
}
.ft-data-item {
    font-size: 11.5px;
    color: #4e7a9a !important;
    margin-bottom: 7px;
    line-height: 1.5;
}
.ft-legal-note {
    display: block;
    font-size: 10px;
    color: #2a4d65 !important;
    line-height: 1.65;
    margin-top: 14px;
    padding-top: 10px;
    border-top: 1px solid #0d1f38;
    font-style: italic;
}

/* ─ Footer nav buttons: rounded, soft blue pill style ─ */
[data-testid="stVerticalBlock"]:has(.ft-nav-section) .stButton > button {
    background: rgba(29, 78, 216, 0.06) !important;
    border: 1px solid rgba(59, 130, 246, 0.18) !important;
    border-radius: 6px !important;
    color: #6aa3c8 !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 7px 12px !important;
    min-height: unset !important;
    height: auto !important;
    line-height: 1.2 !important;
    width: 100% !important;
    box-shadow: none !important;
    letter-spacing: 0.01em !important;
    margin-bottom: 5px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stVerticalBlock"]:has(.ft-nav-section) .stButton > button:hover {
    background: rgba(29, 78, 216, 0.14) !important;
    border-color: rgba(59, 130, 246, 0.45) !important;
    color: #c2dff5 !important;
}
[data-testid="stVerticalBlock"]:has(.ft-nav-section) .stButton > button:focus:not(:active) {
    box-shadow: none !important;
    background: rgba(29, 78, 216, 0.06) !important;
}
[data-testid="stVerticalBlock"]:has(.ft-nav-section) .stButton > button:active {
    background: rgba(29, 78, 216, 0.2) !important;
    color: #d8eeff !important;
}
</style>""", unsafe_allow_html=True)


# ============== HOME VIEW ==============
def show_home():
    st.markdown("""
<div style="text-align: center; padding: 40px 0 30px 0;">
  <h1 style="font-size: 42px;">🏦 AI Financial Advisor</h1>
  <p style="font-size: 18px; color: #8b949e;">Your intelligent assistant for smarter investment decisions</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""<div class="tool-card">
<div style="font-size: 48px; margin-bottom: 15px;">📊</div>
<div style="font-size: 22px; font-weight: 600; color: #e6edf3 !important;">Portfolio Allocator</div>
<p style="color: #8b949e; margin: 15px 0;">Optimize your multi-stock portfolio with AI-powered allocation, risk analytics, and rebalancing recommendations.</p>
<ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
<li>Multi-stock signal analysis</li>
<li>Position sizing &amp; allocation</li>
<li>Risk metrics (Sharpe, Beta, VaR)</li>
<li>Performance vs S&amp;P 500</li>
<li>Dividend income tracking</li>
<li>One-click rebalancing</li>
</ul>
</div>""", unsafe_allow_html=True)
        if st.button("Enter Portfolio Allocator →", key="btn_portfolio", use_container_width=True):
            st.session_state.current_view = "portfolio"
            st.rerun()

    with col2:
        st.markdown("""<div class="tool-card">
<div style="font-size: 48px; margin-bottom: 15px;">📈</div>
<div style="font-size: 22px; font-weight: 600; color: #e6edf3 !important;">Stock Analyzer</div>
<p style="color: #8b949e; margin: 15px 0;">Deep-dive analysis of individual stocks with technical indicators and fundamental metrics to find the best opportunities.</p>
<ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
<li>CFA-style technical analysis (RSI, MACD, Bollinger, ADX)</li>
<li>Fundamental scoring (valuation, profitability, growth, health)</li>
<li>Multi-model valuation (P/E, DCF, analyst consensus)</li>
<li>Return forecasts with confidence intervals</li>
<li>Support &amp; resistance levels</li>
<li>BUY / HOLD / SELL recommendation</li>
</ul>
</div>""", unsafe_allow_html=True)
        if st.button("Enter Stock Analyzer →", key="btn_analyzer", use_container_width=True):
            st.session_state.current_view = "analyzer"
            st.rerun()

    with col3:
        st.markdown("""<div class="tool-card">
<div style="font-size: 48px; margin-bottom: 15px;">📚</div>
<div style="font-size: 22px; font-weight: 600; color: #e6edf3 !important;">Case Q&amp;A</div>
<p style="color: #8b949e; margin: 15px 0;">Chat with your course materials using RAG-powered AI. Every answer is grounded in your uploaded documents with file and page citations.</p>
<ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
<li>Upload PDFs directly in the browser</li>
<li>Auto-indexed — no terminal needed</li>
<li>Ask any question about the materials</li>
<li>Cited answers: file + page + chunk ID</li>
<li>Refuses unsupported questions explicitly</li>
</ul>
</div>""", unsafe_allow_html=True)
        if st.button("Enter Case Q&A →", key="btn_caseqa", use_container_width=True):
            st.session_state.current_view = "caseqa"
            st.rerun()


# ============== MAIN ROUTING ==============
if st.session_state.current_view == "home":
    show_home()
elif st.session_state.current_view == "analyzer":
    from stock_analyzer import show_stock_analyzer
    show_stock_analyzer()
elif st.session_state.current_view == "portfolio":
    import os
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Back", key="back_portfolio"):
            st.session_state.current_view = "home"
            st.rerun()
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "portfolio",
        os.path.join(os.path.dirname(__file__), "portfolio_allocator.py")
    )
    portfolio_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(portfolio_module)
elif st.session_state.current_view == "caseqa":
    from case_qa import show_case_qa
    show_case_qa()


# ============== FOOTER ==============
# Row 1: st.columns() — brand | navigation buttons | data & legal
# Row 2: st.markdown() — copyright strip
# Gap fix: columns padding-bottom = 2rem; copyright margin-top = -2rem.
# The 2rem overlap eats into the columns’ bottom padding (not text content),
# so the copyright always sits flush regardless of Streamlit’s flex gap value.

ft_col1, ft_col2, ft_col3 = st.columns([2, 1, 1.5])

with ft_col1:
    st.markdown("""
<span class="ft-brand-title">🏦 AI FINANCIAL ADVISOR</span>
<span class="ft-brand-body">
  Institutional-grade analytics for portfolio optimization,
  equity research, and document intelligence.
</span>
""", unsafe_allow_html=True)

with ft_col2:
    st.markdown('<span class="ft-section-label">Navigation</span><div class="ft-nav-section"></div>', unsafe_allow_html=True)
    if st.button("Home", key="ft_home"):
        st.session_state.current_view = "home"
        st.rerun()
    if st.button("Portfolio Allocator", key="ft_portfolio"):
        st.session_state.current_view = "portfolio"
        st.rerun()
    if st.button("Stock Analyzer", key="ft_analyzer"):
        st.session_state.current_view = "analyzer"
        st.rerun()
    if st.button("Case Q&A", key="ft_caseqa"):
        st.session_state.current_view = "caseqa"
        st.rerun()

with ft_col3:
    st.markdown("""
<span class="ft-section-label">Data &amp; Legal</span>
<div class="ft-data-item">• Yahoo Finance &mdash; 15–20 min delayed</div>
<div class="ft-data-item">• AI analysis via OpenAI GPT-4o</div>
<div class="ft-data-item">• US-listed equities only</div>
<span class="ft-legal-note">Past performance is not indicative of future results.
Not affiliated with any financial institution.</span>
""", unsafe_allow_html=True)

# Copyright strip — flush below the columns via negative margin
st.markdown("""
<div class="ft-copy">
  <span>© 2025 AI Financial Advisor</span>
  <span class="ft-copy-sep">·</span>
  <span>Educational use only</span>
  <span class="ft-copy-sep">·</span>
  <span>Not financial advice</span>
  <span class="ft-copy-sep">·</span>
  <span>All rights reserved</span>
</div>
""", unsafe_allow_html=True)

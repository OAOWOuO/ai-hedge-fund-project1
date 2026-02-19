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

# ── Keyboard-shortcut navigation via URL query params ──────────────────────────
try:
    _nav = st.query_params.get("nav", "")
    if _nav in ("home", "portfolio", "analyzer", "caseqa"):
        st.session_state["current_view"] = _nav
        st.query_params.clear()
except Exception:
    pass

# Initialize session state for navigation
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

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

    /* ── Sticky footer ── */
    .aifa-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: #010409;
        border-top: 1px solid #21262d;
        padding: 0 28px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.03em;
    }
    .aifa-footer-left {
        display: flex;
        align-items: center;
        gap: 14px;
        color: #6e7681;
        white-space: nowrap;
    }
    .aifa-footer-brand {
        color: #c9d1d9 !important;
        font-weight: 600;
        letter-spacing: 0.08em;
        font-size: 11px;
    }
    .aifa-footer-sep {
        color: #21262d !important;
    }
    .aifa-footer-center {
        display: flex;
        align-items: center;
        gap: 20px;
        color: #6e7681;
        white-space: nowrap;
    }
    .aifa-footer-shortcut-label {
        color: #484f58 !important;
        font-size: 9px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-right: 4px;
    }
    .aifa-footer-shortcut {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: #8b949e !important;
        font-size: 11px;
    }
    .aifa-kbd {
        display: inline-block;
        background: #161b22;
        border: 1px solid #30363d;
        border-bottom: 2px solid #21262d;
        border-radius: 3px;
        padding: 1px 6px;
        font-size: 9px;
        color: #58a6ff !important;
        font-family: 'SF Mono', 'Consolas', monospace;
        letter-spacing: 0.04em;
        line-height: 1.6;
    }
    .aifa-footer-right {
        display: flex;
        align-items: center;
        gap: 14px;
        color: #484f58;
        white-space: nowrap;
        font-size: 10px;
    }
    /* Pad content so footer doesn't overlap */
    .main .block-container {
        padding-bottom: 60px !important;
    }
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

    col1, col2, col3 = st.columns(3, gap="large")

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
                <li>Position sizing &amp; allocation</li>
                <li>Risk metrics (Sharpe, Beta, VaR)</li>
                <li>Performance vs S&amp;P 500</li>
                <li>Dividend income tracking</li>
                <li>One-click rebalancing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Portfolio Allocator →", key="btn_portfolio", use_container_width=True):
            st.session_state.current_view = "portfolio"
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
                <li>CFA-style technical analysis (RSI, MACD, Bollinger, ADX)</li>
                <li>Fundamental scoring (valuation, profitability, growth, health)</li>
                <li>Multi-model valuation (P/E, DCF, analyst consensus)</li>
                <li>Return forecasts with confidence intervals</li>
                <li>Support &amp; resistance levels</li>
                <li>BUY / HOLD / SELL recommendation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Stock Analyzer →", key="btn_analyzer", use_container_width=True):
            st.session_state.current_view = "analyzer"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="tool-card">
            <div style="font-size: 48px; margin-bottom: 15px;">📚</div>
            <div style="font-size: 24px; font-weight: 600; color: #e6edf3 !important;">Case Q&amp;A</div>
            <p style="color: #8b949e; margin: 15px 0;">
                Chat with your course materials using RAG-powered AI.
                Every answer is grounded in your uploaded documents
                with file and page citations.
            </p>
            <ul style="text-align: left; color: #8b949e; padding-left: 20px; font-size: 14px;">
                <li>Upload PDFs directly in the browser</li>
                <li>Auto-indexed — no terminal needed</li>
                <li>Ask any question about the materials</li>
                <li>Cited answers: file + page + chunk ID</li>
                <li>Refuses unsupported questions explicitly</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
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


# ============== STICKY FOOTER (all views) ==============
st.markdown("""
<div class="aifa-footer">
    <div class="aifa-footer-left">
        <span class="aifa-footer-brand">🏦 AI FINANCIAL ADVISOR</span>
        <span class="aifa-footer-sep">&nbsp;│&nbsp;</span>
        <span style="color:#484f58">v1.0</span>
    </div>
    <div class="aifa-footer-center">
        <span class="aifa-footer-shortcut-label">Shortcuts</span>
        <span class="aifa-footer-shortcut"><span class="aifa-kbd">Alt</span><span class="aifa-kbd">H</span>&nbsp;Home</span>
        <span class="aifa-footer-shortcut"><span class="aifa-kbd">Alt</span><span class="aifa-kbd">P</span>&nbsp;Portfolio</span>
        <span class="aifa-footer-shortcut"><span class="aifa-kbd">Alt</span><span class="aifa-kbd">S</span>&nbsp;Stock Analyzer</span>
        <span class="aifa-footer-shortcut"><span class="aifa-kbd">Alt</span><span class="aifa-kbd">C</span>&nbsp;Case Q&amp;A</span>
    </div>
    <div class="aifa-footer-right">
        <span>Yahoo Finance &bull; 15-20 min delay</span>
        <span style="color:#21262d">&nbsp;│&nbsp;</span>
        <span>For educational use only &bull; Not financial advice</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Keyboard shortcut JavaScript ───────────────────────────────────────────────
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    function navigateTo(view) {
        try {
            var url = new URL(window.parent.location.href);
            url.searchParams.set('nav', view);
            window.parent.location.href = url.toString();
        } catch(e) {}
    }
    window.parent.document.addEventListener('keydown', function(e) {
        if (e.altKey && !e.ctrlKey && !e.metaKey) {
            switch(e.key.toLowerCase()) {
                case 'h': e.preventDefault(); navigateTo('home'); break;
                case 'p': e.preventDefault(); navigateTo('portfolio'); break;
                case 's': e.preventDefault(); navigateTo('analyzer'); break;
                case 'c': e.preventDefault(); navigateTo('caseqa'); break;
            }
        }
    }, { once: false });
})();
</script>
""", height=0)

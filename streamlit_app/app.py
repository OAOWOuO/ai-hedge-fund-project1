"""
AI Financial Advisor
Combined app with session state navigation
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Keyboard-shortcut navigation via URL query params ──────────────────────
try:
    _nav = st.query_params.get("nav", "")
    if _nav in ("home", "portfolio", "analyzer", "caseqa"):
        st.session_state["current_view"] = _nav
        st.query_params.clear()
except Exception:
    pass

if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

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


# ============== FOOTER ─────────────────────────────────────────────────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    background: transparent;
    overflow: hidden;
    /* Distinct from app — deep midnight navy, not the same dark gray */
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  }

  /* ── Accent bar at very top ── */
  .ft-accent {
    height: 3px;
    background: linear-gradient(90deg, #0f2a4a 0%, #1d4ed8 40%, #3b82f6 60%, #0f2a4a 100%);
  }

  /* ── Main footer body ── */
  .ft-body {
    background: #05091a;
    border-top: 1px solid #0d1f38;
  }

  /* ── Four-column grid with vertical dividers ── */
  .ft-grid {
    display: grid;
    grid-template-columns: 1.9fr 1fr 1.25fr 1.45fr;
    padding: 44px 56px 38px;
  }

  .ft-col {
    padding: 0 40px;
  }
  .ft-col:first-child { padding-left: 0; }
  .ft-col:last-child  { padding-right: 0; }
  .ft-col:not(:last-child) {
    border-right: 1px solid #0d1f38;
  }

  /* ── Column section label ── */
  .ft-label {
    display: block;
    font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #2563eb;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #0d1f38;
  }

  /* ── Brand column ── */
  .ft-brand-name {
    display: block;
    font-family: 'SF Mono', 'Consolas', 'Liberation Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #c8d8ea;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #0d1f38;
  }
  .ft-brand-desc {
    display: block;
    font-size: 12.5px;
    line-height: 1.75;
    color: #4a6880;
    margin-bottom: 10px;
  }
  .ft-brand-sub {
    display: block;
    font-size: 11px;
    line-height: 1.75;
    color: #293d52;
  }

  /* ── Navigation buttons ── */
  .ft-nav {
    display: block;
    font-size: 12.5px;
    line-height: 1;
    color: #4a6880;
    text-decoration: none;
    padding: 8px 0 8px 12px;
    margin-bottom: 2px;
    border-left: 2px solid transparent;
    transition: color 0.15s ease, border-color 0.15s ease;
    cursor: pointer;
    letter-spacing: 0.01em;
  }
  .ft-nav:hover {
    color: #c8d8ea;
    border-left-color: #2563eb;
    text-decoration: none;
  }

  /* ── Keyboard shortcut rows ── */
  .sc-row {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 11px;
    padding-left: 2px;
  }
  .kbd {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 28px;
    height: 20px;
    padding: 0 6px;
    background: #0a1628;
    border: 1px solid #1a3050;
    border-bottom: 2px solid #0d1f38;
    border-radius: 3px;
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 9px;
    font-weight: 600;
    color: #3b82f6;
    letter-spacing: 0.06em;
  }
  .sc-desc {
    font-size: 11.5px;
    color: #3d5a72;
    margin-left: 4px;
    letter-spacing: 0.01em;
  }

  /* ── Data & Legal column ── */
  .ft-data-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 11.5px;
    color: #3d5a72;
    margin-bottom: 10px;
    line-height: 1.5;
    letter-spacing: 0.01em;
  }
  .ft-data-icon {
    flex-shrink: 0;
    font-size: 11px;
    margin-top: 1px;
    opacity: 0.7;
  }
  .ft-disclaimer {
    display: block;
    font-size: 10.5px;
    color: #1e3048;
    line-height: 1.75;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #0a1628;
    font-style: italic;
    letter-spacing: 0.01em;
  }

  /* ── Copyright strip ── */
  .ft-copy {
    background: #030712;
    border-top: 1px solid #0a1628;
    padding: 12px 56px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 10px;
    color: #1e3048;
    letter-spacing: 0.05em;
  }
  .ft-copy-sep {
    color: #0d1f38;
    font-size: 12px;
  }
</style>
</head>
<body>

<div class="ft-accent"></div>

<div class="ft-body">
  <div class="ft-grid">

    <!-- Column 1: Brand -->
    <div class="ft-col">
      <span class="ft-brand-name">&#127974;&ensp;AI FINANCIAL ADVISOR</span>
      <span class="ft-brand-desc">
        Institutional-grade investment analytics for portfolio
        optimization, equity research, and document intelligence.
      </span>
      <span class="ft-brand-sub">
        Built for students and practitioners seeking professional-quality
        financial analysis tools powered by modern AI.
      </span>
    </div>

    <!-- Column 2: Navigation -->
    <div class="ft-col">
      <span class="ft-label">Navigation</span>
      <a class="ft-nav" data-nav="home">Home</a>
      <a class="ft-nav" data-nav="portfolio">Portfolio Allocator</a>
      <a class="ft-nav" data-nav="analyzer">Stock Analyzer</a>
      <a class="ft-nav" data-nav="caseqa">Case Q&amp;A</a>
    </div>

    <!-- Column 3: Keyboard Shortcuts -->
    <div class="ft-col">
      <span class="ft-label">Keyboard Shortcuts</span>
      <div class="sc-row">
        <span class="kbd">Alt</span><span class="kbd">H</span>
        <span class="sc-desc">Home</span>
      </div>
      <div class="sc-row">
        <span class="kbd">Alt</span><span class="kbd">P</span>
        <span class="sc-desc">Portfolio Allocator</span>
      </div>
      <div class="sc-row">
        <span class="kbd">Alt</span><span class="kbd">S</span>
        <span class="sc-desc">Stock Analyzer</span>
      </div>
      <div class="sc-row">
        <span class="kbd">Alt</span><span class="kbd">C</span>
        <span class="sc-desc">Case Q&amp;A</span>
      </div>
    </div>

    <!-- Column 4: Data & Legal -->
    <div class="ft-col">
      <span class="ft-label">Data &amp; Legal</span>
      <div class="ft-data-row">
        <span class="ft-data-icon">&#8227;</span>
        <span>Market data sourced from Yahoo Finance</span>
      </div>
      <div class="ft-data-row">
        <span class="ft-data-icon">&#8227;</span>
        <span>Equity prices delayed 15&ndash;20 minutes</span>
      </div>
      <div class="ft-data-row">
        <span class="ft-data-icon">&#8227;</span>
        <span>AI signals generated via OpenAI GPT-4o</span>
      </div>
      <div class="ft-data-row">
        <span class="ft-data-icon">&#8227;</span>
        <span>Coverage restricted to US-listed equities</span>
      </div>
      <span class="ft-disclaimer">
        This platform is provided for educational purposes only and does
        not constitute financial, investment, or legal advice. Past
        performance is not indicative of future results.
      </span>
    </div>

  </div>

  <!-- Copyright strip -->
  <div class="ft-copy">
    <span>&copy; 2025 AI Financial Advisor</span>
    <span class="ft-copy-sep">|</span>
    <span>Not affiliated with any registered financial institution</span>
    <span class="ft-copy-sep">|</span>
    <span>For educational use only</span>
    <span class="ft-copy-sep">|</span>
    <span>All rights reserved</span>
  </div>
</div>

<script>
(function () {
  function goTo(view) {
    try {
      var url = new URL(window.parent.location.href);
      url.searchParams.set('nav', view);
      window.parent.location.href = url.toString();
    } catch (e) {}
  }

  document.querySelectorAll('.ft-nav[data-nav]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      goTo(el.getAttribute('data-nav'));
    });
  });

  try {
    window.parent.document.addEventListener('keydown', function (e) {
      if (e.altKey && !e.ctrlKey && !e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'h': e.preventDefault(); goTo('home'); break;
          case 'p': e.preventDefault(); goTo('portfolio'); break;
          case 's': e.preventDefault(); goTo('analyzer'); break;
          case 'c': e.preventDefault(); goTo('caseqa'); break;
        }
      }
    });
  } catch (e) {}
})();
</script>

</body>
</html>
""", height=310, scrolling=False)

"""
pages/2_DataSynthX.py — Synthetic Data Platform
─────────────────────────────────────────────────────────────────────────────
Wraps the original DataSynthX app.py into the Bayantx360 multipage structure.

Changes from standalone:
  • Auth/credit system replaced by utils.auth (shared module)
  • Session state keys use bx360_ prefix
  • deduct_credit() / deduct_credits_amount() → spend_credits("datasynthx")
  • Sign-out calls utils.auth.logout()
  • All data generation logic is unchanged
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, sys, os, warnings, re
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.auth import (
    is_authenticated, is_free_trial, current_credits,
    validate_key, login_free_trial, login_with_key,
    spend_credits, refresh_credits, logout,
)

st.set_page_config(
    page_title="DataSynthX",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #1a1a24;
    --border: #2a2a3a;
    --accent: #7c6af7;
    --accent2: #3ecfcf;
    --accent3: #f76a6a;
    --text: #e8e8f0;
    --muted: #6b6b80;
}

html, body, [class*="css"] {
    background-color: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
}

.stApp { background: var(--bg); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Header */
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.brand-logo {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}
.brand-name {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.brand-tag {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: -4px;
}

/* Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
}
.metric-sub {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
}

/* Score gauge */
.sci-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
}
.sci-ring {
    width: 160px; height: 160px;
    margin: 0 auto 16px;
    position: relative;
}
.sci-score {
    font-size: 48px;
    font-weight: 800;
    line-height: 1;
}
.sci-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    color: var(--muted);
    text-transform: uppercase;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    padding: 8px 20px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), #6055d4) !important;
    color: white !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #6055d4);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(124, 106, 247, 0.35);
}

/* Download button */
.stDownloadButton > button {
    background: var(--surface2);
    color: var(--accent2);
    border: 1px solid var(--accent2);
    border-radius: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    width: 100%;
}

/* Reset Analysis button — orange outline, distinct from Sign Out */
[data-testid="stSidebar"] [data-testid="stButton-reset_analysis_btn"] > button {
    background: transparent !important;
    color: #f7a86a !important;
    border: 1px solid #f7a86a !important;
    font-size: 12px !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 0.5px !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton-reset_analysis_btn"] > button:hover {
    background: rgba(247,168,106,0.08) !important;
    box-shadow: 0 0 12px rgba(247,168,106,0.2) !important;
    transform: none !important;
}

/* Inputs */
.stNumberInput input, .stSlider, .stSelectbox select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* File uploader */
.stFileUploader {
    background: var(--surface);
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 20px;
}

/* Section headers */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
    margin-left: 8px;
}
.section-sub {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* Status badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-green { background: rgba(62,207,207,0.1); color: var(--accent2); border: 1px solid rgba(62,207,207,0.3); }
.badge-purple { background: rgba(124,106,247,0.1); color: var(--accent); border: 1px solid rgba(124,106,247,0.3); }
.badge-red { background: rgba(247,106,106,0.1); color: var(--accent3); border: 1px solid rgba(247,106,106,0.3); }

/* Tables */
.stDataFrame { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
thead th { background: var(--surface2) !important; }

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 4px; }

/* Dividers */
hr { border-color: var(--border); }

/* Plotly charts */
.js-plotly-plot .plotly { background: transparent !important; }

/* Hide Streamlit branding — keep sidebar toggle visible */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
/* Only hide the Deploy/toolbar portion of the header, NOT the whole header
   so the sidebar collapse «« button remains functional */
header[data-testid="stHeader"] {
    background: transparent !important;
}
header[data-testid="stHeader"]::before {
    display: none;
}
/* Hide toolbar safely */
/* Target ALL sidebar toggle states */
button[kind="header"],
div[data-testid="collapsedControl"],
button[data-testid="collapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 9999 !important;
    cursor: pointer !important;
}
</style>
""")


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH GATE
# ═══════════════════════════════════════════════════════════════════════════════
if not is_authenticated():
    def render_landing():
        st.html("""
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        .block-container { max-width: 980px; margin: 0 auto; padding-top: 2rem; }
        </style>""")
    
        # Hero
        st.html("""
        <div style="text-align:center;padding:60px 20px 40px;">
            <div style="display:inline-flex;align-items:center;gap:12px;margin-bottom:28px;">
                <div style="width:46px;height:46px;background:linear-gradient(135deg,#7c6af7,#3ecfcf);
                            clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
                            flex-shrink:0;"></div>
                <span style="font-family:Syne,sans-serif;font-size:28px;font-weight:800;
                             background:linear-gradient(90deg,#7c6af7,#3ecfcf);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    DataSynthX
                </span>
            </div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#3ecfcf;
                        letter-spacing:3px;text-transform:uppercase;margin-bottom:18px;">
                Privacy-Safe · Statistically Reliable · Trustworthy Data
            </div>
            <h1 style="font-family:Syne,sans-serif;font-size:30px;font-weight:800;
                       background:linear-gradient(135deg,#e8e8f0 40%,#7c6af7);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       line-height:1.1;margin:0 0 22px;">
                Generate Synthetic Data<br>That Mirrors The Original Data
            </h1>
            <p style="font-family:Syne,sans-serif;font-size:17px;color:#9999b0;
                      max-width:580px;margin:0 auto 50px;line-height:1.75;">
                Upload any dataset. DataSynthX learns its statistical DNA — distributions,
                correlations, categories — and generates unlimited privacy-safe synthetic
                dataset at any scale with measurable fidelity.
            </p>
        </div>
        """)
    
        # How it works strip
        st.html("""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px;
                    max-width:860px;margin:0 auto 64px;">
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:14px;
                        padding:28px 22px;text-align:center;">
                <div style="font-size:32px;margin-bottom:12px;">⬆</div>
                <div style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;
                            color:#e8e8f0;margin-bottom:8px;">Upload</div>
                <div style="font-family:Space Mono,monospace;font-size:13px;color:#6b6b80;line-height:1.7;">
                    Drop any CSV or Excel file (e.g. Survey/Experimental Data). Every column is profiled automatically — numeric,
                    categorical, datetime.
                </div>
            </div>
            <div style="background:#111118;border:1px solid #2a2a3a;border-top:2px solid #7c6af7;
                        border-radius:14px;padding:28px 22px;text-align:center;">
                <div style="font-size:32px;margin-bottom:12px;">⬡</div>
                <div style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;
                            color:#e8e8f0;margin-bottom:8px;">Generate</div>
                <div style="font-family:Space Mono,monospace;font-size:13px;color:#6b6b80;line-height:1.7;">
                    Multivariate Gaussian + frequency-preserving sampling. Scale to millions
                    of rows instantly.
                </div>
            </div>
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:14px;
                        padding:28px 22px;text-align:center;">
                <div style="font-size:32px;margin-bottom:12px;">⬇</div>
                <div style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;
                            color:#e8e8f0;margin-bottom:8px;">Export & Verify</div>
                <div style="font-family:Space Mono,monospace;font-size:13px;color:#6b6b80;line-height:1.7;">
                    Download CSV / Excel. The SCI score validates statistical fidelity
                    across every column.
                </div>
            </div>
        </div>
        """)
    
        # Free Trial CTA — appears before pricing
        st.html("""
        <div style="max-width:860px;margin:0 auto 16px;padding:0 20px;">
            <div style="background:linear-gradient(135deg,rgba(124,106,247,0.08),rgba(62,207,207,0.07));
                        border:1px solid rgba(124,106,247,0.28);border-radius:18px;
                        padding:36px 32px;position:relative;overflow:hidden;text-align:center;">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;
                            background:linear-gradient(90deg,transparent,#7c6af7 40%,#3ecfcf 60%,transparent);"></div>
                <div style="font-family:Space Mono,monospace;font-size:10px;color:#3ecfcf;
                            letter-spacing:3px;text-transform:uppercase;margin-bottom:14px;">
                    ⬡ No credit card required · Instant access
                </div>
                <div style="font-family:Syne,sans-serif;font-size:26px;font-weight:800;
                            background:linear-gradient(90deg,#e8e8f0,#7c6af7);
                            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                            margin-bottom:10px;line-height:1.15;">
                    Start Free or Use Trial Version
                </div>
                <p style="font-family:Space Mono,monospace;font-size:12px;color:#9999b0;
                          max-width:520px;margin:0 auto 24px;line-height:1.9;">
                    Upload data, generate synthetic datasets and explore all results — completely free.
                    Upgrade to unlock AI Explainer and full Excel exports.
                </p>
                <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-bottom:28px;">
                    <span style="background:rgba(62,207,207,0.1);border:1px solid rgba(62,207,207,0.25);
                                 color:#3ecfcf;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;">
                        ✓ Upload CSV / Excel
                    </span>
                    <span style="background:rgba(62,207,207,0.1);border:1px solid rgba(62,207,207,0.25);
                                 color:#3ecfcf;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;">
                        ✓ Generate Synthetic Data
                    </span>
                    <span style="background:rgba(62,207,207,0.1);border:1px solid rgba(62,207,207,0.25);
                                 color:#3ecfcf;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;">
                        ✓ View All Results & Trust Metrics
                    </span>
                    <span style="background:rgba(62,207,207,0.1);border:1px solid rgba(62,207,207,0.25);
                                 color:#3ecfcf;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;">
                        ✓ CSV &amp; Excel Export (≤70 rows)
                    </span>
                    <span style="background:rgba(247,106,106,0.08);border:1px solid rgba(247,106,106,0.2);
                                 color:#f76a6a;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;opacity:0.85;">
                        ✗ CSV / Excel Export &gt;70 rows
                    </span>
                    <span style="background:rgba(247,106,106,0.08);border:1px solid rgba(247,106,106,0.2);
                                 color:#f76a6a;font-family:Space Mono,monospace;font-size:10px;
                                 letter-spacing:1px;padding:6px 14px;border-radius:8px;opacity:0.85;">
                        ✗ AI Explainer
                    </span>
                </div>
            </div>
        </div>
        """)
    
        _, trial_col, _ = st.columns([1.2, 1, 1.2])
        with trial_col:
            trial_btn = st.button("⬡ Start Free Trial", type="primary", width='stretch', key="trial_btn")
    
        st.html("<div style='margin-bottom:40px;'></div>")
    
        if trial_btn:
            login_free_trial("datasynthx")
            # handled by login_free_trial
            # handled by login_free_trial
            # handled by login_free_trial
            st.session_state["key_plan"]       = "Free Trial"
            # handled by login_free_trial
            st.rerun()
    
        # Pricing header
        st.html("""
        <div style="text-align:center;margin-bottom:36px;">
            <div style="font-family:Space Mono,monospace;font-size:16px;color:#6b6b80;
                        letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Upgrade: Pricing & Payment</div>
            <div style="font-family:Syne,sans-serif;font-size:30px;font-weight:800;color:#e8e8f0;">
                Simple, credit-based access
            </div>
            <div style="font-family:Space Mono,monospace;font-size:16px;color:#6b6b80;margin-top:8px;">
                Buy once, use at your own pace. Each generation run costs 1 credit.
                Access key is emailed after purchase.
            </div>
        </div>
        """)
    
        # Pricing cards
        p_cols = st.columns(3, gap="medium")
        for col, plan in zip(p_cols, PLANS):
            border_top = f"border-top:3px solid {plan['color']};" if plan["highlight"] else f"border-top:2px solid {plan['color']}55;"
            shadow     = f"box-shadow:0 12px 48px {plan['color']}28;" if plan["highlight"] else ""
            badge_html = (
                f'<div style="background:rgba(124,106,247,0.15);color:#7c6af7;font-family:Space Mono,monospace;'
                f'font-size:9px;letter-spacing:2px;text-transform:uppercase;padding:3px 12px;'
                f'border-radius:20px;display:inline-block;margin-bottom:14px;">★ MOST POPULAR</div>'
                if plan["highlight"] else "<div style='height:26px;'></div>"
            )
            feats = "".join(
                f'<div style="font-family:Space Mono,monospace;font-size:11px;color:#9999b0;'
                f'padding:6px 0;border-bottom:1px solid #1e1e2a;">'
                f'<span style="color:{plan["color"]};margin-right:8px;">✓</span>{f}</div>'
                for f in plan["features"]
            )
            with col:
                st.html(f"""
                <div style="background:#111118;border:1px solid #2a2a3a;{border_top}
                            border-radius:16px;padding:32px 24px 12px;{shadow}height:100%;box-sizing:border-box;">
                    {badge_html}
                    <div style="font-family:Syne,sans-serif;font-size:19px;font-weight:800;
                                color:#e8e8f0;margin-bottom:6px;">{plan["name"]}</div>
                    <div style="font-family:Syne,sans-serif;font-size:44px;font-weight:800;
                                color:{plan["color"]};line-height:1;margin:10px 0 4px;">{plan["price"]}</div>
                    <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                margin-bottom:22px;">{plan["credits"]} credits · {plan["period"]}</div>
                    <div style="margin-bottom:12px;">{feats}</div>
                </div>
                """)
                st.link_button(
                    f"Get {plan['name']} Access →",
                    url=plan["link"],
                    width='stretch',
                )
    
        # Access key entry
        st.html("""
        <div style="text-align:center;margin-top:64px;margin-bottom:20px;">
            <div style="font-family:Space Mono,monospace;font-size:16px;color:#6b6b80;
                        letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">
                Already have an access key?
            </div>
            <div style="font-family:Space Mono,monospace;font-size:14px;color:#3a3a50;">
                Your key is emailed to you after purchase.
            </div>
        </div>
        """)
    
        _, c, _ = st.columns([1, 2, 1])
        with c:
            key_input = st.text_input(
                "Access Key",
                placeholder="DSX-XXXX-XXXX-XXXX",
                label_visibility="collapsed",
                key="landing_key_input",
            )
            enter_btn = st.button("⬡ Enter DataSynthX", type="primary", width='stretch')
    
            if enter_btn:
                if not key_input.strip():
                    st.error("Please enter your access key.")
                else:
                    with st.spinner("Validating key…"):
                        row = validate_key(key_input.strip())
                    if row is None:
                        st.error("Invalid access key. Please check and try again.")
                    elif int(row.get(COL_CREDITS, 0)) <= 0:
                        st.error("Your key has 0 credits remaining. Please contact support to top up.")
                    else:
                        login_free_trial("datasynthx")
                        # handled by login_with_key
                        # handled by login_with_key
                        st.session_state["key_plan"]      = "—"
                        # handled by login_with_key
                        st.rerun()
    
    
        st.html("""
        <div style="text-align:center;font-family:Space Mono,monospace;font-size:10px;
                    color:#2e2e3e;margin-top:56px;letter-spacing:1px;padding-bottom:40px;">
            DataSynthX: Your Privacy-first synthetic data solution 
        </div>
        """)
    
        st.markdown("""
        <style>
        .gate-links a {
            text-decoration: none;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, #0e75b6, #0b5ed7);
            padding: 10px 16px;
            border-radius: 8px;
            margin: 0 6px;
            display: inline-block;
            transition: 0.2s ease;
         }
         .gate-links a:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
         }
         .gate-sep {
            display: none;
         }
         </style>
    
         <div style="text-align:center;" class="gate-links">
             <a href="https://x.com/bayantx360" target="_blank">👤 Get Access Key</a>
             <a href="#" target="_blank">📋 User Guide</a>
             <a href="mailto:bayantx360@gmail.com">⚙️ Support</a>
        </div>
        """, unsafe_allow_html=True)
        
    
        st.html("""
        <div style="text-align:center;font-family:Space Mono,monospace;font-size:10px;
                    color:#2e2e3e;margin-top:56px;letter-spacing:1px;padding-bottom:40px;">
            © 2025 DataSynthX · Privacy-first synthetic data
        </div>
        """)
    
    
    
    # ─── Auth gate ────────────────────────────────────────────────────────────────

    st.stop()

# ── Refresh credits on every load (paid users) ────────────────────────────────
if not st.session_state.get("bx360_is_free_trial", False):
    refresh_credits("datasynthx")

# ═══════════════════════════════════════════════════════════════════════════
#  CORENGINES
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════

class DataProfiler:
    """Compute statistical profile of uploaded dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        # Try to parse datetime columns
        self.datetime_cols = []
        for col in self.categorical_cols[:]:
            try:
                parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors='coerce')
                if parsed.notna().sum() > len(df) * 0.7:
                    self.datetime_cols.append(col)
                    self.categorical_cols.remove(col)
            except Exception:
                pass

    def profile(self) -> dict:
        p = {}
        # Numeric stats
        p['numeric_stats'] = {}
        for col in self.numeric_cols:
            s = self.df[col].dropna()
            p['numeric_stats'][col] = {
                'mean': float(s.mean()),
                'std': float(s.std()),
                'variance': float(s.var()),
                'min': float(s.min()),
                'max': float(s.max()),
                'skew': float(s.skew()),
                'kurtosis': float(s.kurtosis()),
                'missing_ratio': float(self.df[col].isna().mean()),
                'values': s.values
            }

        # Categorical stats
        p['categorical_stats'] = {}
        for col in self.categorical_cols:
            s = self.df[col].dropna()
            freq = s.value_counts(normalize=True)
            p['categorical_stats'][col] = {
                'frequencies': freq.to_dict(),
                'n_unique': int(s.nunique()),
                'missing_ratio': float(self.df[col].isna().mean()),
                'mode': str(s.mode().iloc[0]) if len(s) > 0 else None
            }

        # Correlation matrix
        if len(self.numeric_cols) >= 2:
            p['correlation_matrix'] = self.df[self.numeric_cols].corr().fillna(0)
        else:
            p['correlation_matrix'] = pd.DataFrame()

        p['shape'] = self.df.shape
        p['numeric_cols'] = self.numeric_cols
        p['categorical_cols'] = self.categorical_cols
        p['datetime_cols'] = self.datetime_cols
        p['missing_overview'] = self.df.isna().mean().to_dict()

        return p


class SyntheticDataGenerator:
    """Generate synthetic data preserving statistical structure."""

    def __init__(self, df: pd.DataFrame, profile: dict):
        self.df = df
        self.profile = profile
        self.numeric_cols = profile['numeric_cols']
        self.categorical_cols = profile['categorical_cols']

    def generate(self, n_rows: int, noise_level: float = 0.02) -> pd.DataFrame:
        synthetic = {}

        # ── Numeric: Multivariate Gaussian ──────────────────────────────
        if self.numeric_cols:
            clean = self.df[self.numeric_cols].dropna()
            n_num = len(self.numeric_cols)
            if len(clean) >= 2:
                # Use fillna(0) + .copy() so NaN-heavy datasets don't produce
                # a read-only NaN matrix that crashes np.eye addition downstream.
                mean_vec = clean.mean().fillna(0).values
                cov_matrix = clean.cov().fillna(0).values.copy()
                # Ensure strictly 2-D square array before adding identity matrix.
                # Guards against: read-only arrays, scalar from single-column cov(),
                # and shape mismatches.
                cov_matrix = np.atleast_2d(cov_matrix).reshape(n_num, n_num)
                cov_matrix += np.eye(n_num) * 1e-8

                try:
                    samples = np.random.multivariate_normal(mean_vec, cov_matrix, n_rows)
                except (np.linalg.LinAlgError, ValueError):
                    # Fallback: independent per-column sampling (catches both
                    # LinAlgError from bad matrices AND ValueError from NaN cov)
                    samples = np.column_stack([
                        np.random.normal(
                            self.profile['numeric_stats'][c]['mean'],
                            max(self.profile['numeric_stats'][c]['std'], 1e-6),
                            n_rows
                        ) for c in self.numeric_cols
                    ])
                # Ensure samples is always 2-D (edge case: single column)
                samples = np.atleast_2d(samples).reshape(n_rows, n_num)

                # Add controlled noise
                noise = np.random.normal(0, noise_level, samples.shape)
                noise *= np.std(samples, axis=0, keepdims=True)
                samples = samples + noise

                # Clip to [min, max] of original
                for i, col in enumerate(self.numeric_cols):
                    stats_c = self.profile['numeric_stats'][col]
                    col_range = stats_c['max'] - stats_c['min']
                    lo = stats_c['min'] - col_range * 0.05
                    hi = stats_c['max'] + col_range * 0.05
                    samples[:, i] = np.clip(samples[:, i], lo, hi)

                    # Preserve integer dtype if original was integer
                    orig_dtype = self.df[col].dtype
                    if np.issubdtype(orig_dtype, np.integer):
                        synthetic[col] = np.round(samples[:, i]).astype(int)
                    else:
                        synthetic[col] = samples[:, i]
            else:
                # Too few rows — independent sampling
                for col in self.numeric_cols:
                    s = self.profile['numeric_stats'][col]
                    synthetic[col] = np.random.normal(s['mean'], max(s['std'], 1e-6), n_rows)

        # ── Categorical: Frequency-preserving sampling ───────────────────
        for col in self.categorical_cols:
            cat_stats = self.profile['categorical_stats'][col]
            categories = list(cat_stats['frequencies'].keys())
            probs = list(cat_stats['frequencies'].values())
            # Normalize probs
            probs = np.array(probs, dtype=float)
            probs /= probs.sum()
            synthetic[col] = np.random.choice(categories, size=n_rows, p=probs)

        # ── Inject missing values proportionally ────────────────────────
        for col in self.numeric_cols + self.categorical_cols:
            missing_ratio = self.profile['missing_overview'].get(col, 0)
            if missing_ratio > 0:
                mask = np.random.rand(n_rows) < missing_ratio
                synth_series = pd.Series(synthetic[col])
                synth_series[mask] = np.nan
                synthetic[col] = synth_series.values

        synth_df = pd.DataFrame(synthetic)
        # Restore original column order where possible
        orig_cols = [c for c in self.df.columns if c in synth_df.columns]
        return synth_df[orig_cols]


class TrustMetrics:
    """Compute trust / fidelity metrics between original and synthetic data."""

    def __init__(self, original: pd.DataFrame, synthetic: pd.DataFrame, profile: dict):
        self.orig = original
        self.synth = synthetic
        self.profile = profile
        self.numeric_cols = profile['numeric_cols']
        self.categorical_cols = profile['categorical_cols']

    def correlation_preservation_score(self) -> tuple[float, pd.DataFrame, pd.DataFrame]:
        if len(self.numeric_cols) < 2:
            return 1.0, pd.DataFrame(), pd.DataFrame()
        orig_corr = self.orig[self.numeric_cols].corr().fillna(0)
        synth_corr = self.synth[self.numeric_cols].corr().fillna(0)
        diff = np.abs(orig_corr.values - synth_corr.values)
        score = max(0.0, 1.0 - diff.mean())
        return float(score), orig_corr, synth_corr

    def distribution_similarity_scores(self) -> dict:
        scores = {}
        for col in self.numeric_cols:
            a = self.orig[col].dropna().values
            b = self.synth[col].dropna().values
            if len(a) < 2 or len(b) < 2:
                scores[col] = {'ks_stat': 0, 'ks_pvalue': 1, 'wasserstein': 0, 'score': 1.0}
                continue
            ks_stat, ks_p = ks_2samp(a, b)
            # Normalize Wasserstein by std of original
            std_a = np.std(a)
            w_dist = wasserstein_distance(a, b) / (std_a + 1e-9)
            score = max(0.0, 1.0 - ks_stat)
            scores[col] = {
                'ks_stat': float(ks_stat),
                'ks_pvalue': float(ks_p),
                'wasserstein': float(w_dist),
                'score': float(score)
            }
        return scores

    def categorical_fidelity_scores(self) -> dict:
        scores = {}
        for col in self.categorical_cols:
            orig_freq = self.orig[col].value_counts(normalize=True)
            synth_freq = self.synth[col].value_counts(normalize=True)
            all_cats = set(orig_freq.index) | set(synth_freq.index)
            p = np.array([orig_freq.get(c, 1e-10) for c in all_cats])
            q = np.array([synth_freq.get(c, 1e-10) for c in all_cats])
            p /= p.sum(); q /= q.sum()
            # KL divergence (clipped)
            kl_div = float(np.sum(p * np.log((p + 1e-10) / (q + 1e-10))))
            kl_div = min(kl_div, 10.0)
            score = max(0.0, 1.0 - kl_div / 10.0)
            scores[col] = {
                'kl_divergence': kl_div,
                'score': float(score),
                'orig_freq': orig_freq.to_dict(),
                'synth_freq': synth_freq.to_dict()
            }
        return scores

    def compute_sci(self) -> dict:
        """Structural Consistency Index — weighted composite score 0–100."""
        corr_score, orig_corr, synth_corr = self.correlation_preservation_score()
        dist_scores = self.distribution_similarity_scores()
        cat_scores = self.categorical_fidelity_scores()

        avg_dist = np.mean([v['score'] for v in dist_scores.values()]) if dist_scores else 1.0
        avg_cat = np.mean([v['score'] for v in cat_scores.values()]) if cat_scores else 1.0

        # Weights
        w_corr, w_dist, w_cat = 0.30, 0.40, 0.30
        if not dist_scores: w_corr, w_dist, w_cat = 0.40, 0.0, 0.60
        if not cat_scores: w_corr, w_dist, w_cat = 0.35, 0.65, 0.0
        if not dist_scores and not cat_scores: w_corr, w_dist, w_cat = 1.0, 0.0, 0.0

        sci_raw = w_corr * corr_score + w_dist * avg_dist + w_cat * avg_cat
        sci = round(sci_raw * 100, 1)

        return {
            'sci': sci,
            'correlation_score': round(corr_score * 100, 1),
            'distribution_score': round(avg_dist * 100, 1),
            'categorical_score': round(avg_cat * 100, 1),
            'orig_corr': orig_corr,
            'synth_corr': synth_corr,
            'dist_scores': dist_scores,
            'cat_scores': cat_scores,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def score_color(score: float) -> str:
    if score >= 85: return "#3ecfcf"
    if score >= 65: return "#7c6af7"
    return "#f76a6a"

def score_badge(score: float) -> str:
    if score >= 85: return "badge-green", "EXCELLENT"
    if score >= 65: return "badge-purple", "GOOD"
    return "badge-red", "NEEDS REVIEW"

def render_heatmap(corr_df: pd.DataFrame, title: str) -> None:
    """Render a correlation heatmap using Plotly — works reliably inside st.columns()."""
    MAX_COLS = 30

    cols = list(corr_df.columns)
    n_total = len(cols)

    if n_total == 0:
        st.caption("Not enough numeric columns for correlation.")
        return

    truncated = n_total > MAX_COLS
    cols = cols[:MAX_COLS]
    corr_df = corr_df.loc[cols, cols]
    n = len(cols)

    z      = corr_df.values.tolist()
    labels = list(cols)

    # Custom purple/teal colourscale matching the app theme
    colorscale = [
        [0.0,  "rgb(247,106,106)"],   # strong negative  → red
        [0.5,  "rgb(17,17,24)"],      # zero             → near-black bg
        [1.0,  "rgb(124,106,247)"],   # strong positive  → purple
    ]

    text_vals = [[f"{v:.2f}" for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=labels,
        y=labels,
        text=text_vals if n <= 20 else None,
        texttemplate="%{text}" if n <= 20 else None,
        textfont={"size": max(7, 11 - n // 4), "color": "white"},
        colorscale=colorscale,
        zmin=-1, zmax=1,
        showscale=True,
        colorbar=dict(
            thickness=12,
            len=0.8,
            tickfont=dict(color="#6b6b80", size=9),
            tickvals=[-1, -0.5, 0, 0.5, 1],
            outlinewidth=0,
        ),
        hoverongaps=False,
        hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
    ))

    chart_px = max(300, min(520, 30 * n + 80))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Space Mono, monospace", size=10,
                      color="#6b6b80"),
            x=0, xanchor="left", pad=dict(b=12),
        ),
        paper_bgcolor="#111118",
        plot_bgcolor="#111118",
        margin=dict(l=10, r=10, t=40, b=10),
        width=None,   # let Streamlit control width
        height=chart_px,
        xaxis=dict(
            tickfont=dict(size=max(7, 10 - n // 6), color="#9999b0",
                          family="Space Mono, monospace"),
            tickangle=-45,
            showgrid=False, zeroline=False,
            side="bottom",
        ),
        yaxis=dict(
            tickfont=dict(size=max(7, 10 - n // 6), color="#9999b0",
                          family="Space Mono, monospace"),
            showgrid=False, zeroline=False,
            autorange="reversed",
        ),
        font=dict(color="#e8e8f0"),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if truncated:
        st.caption(f"Showing first {MAX_COLS} of {n_total} columns.")


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SyntheticData')
        wb = writer.book
        ws = writer.sheets['SyntheticData']
        header_fmt = wb.add_format({'bold': True, 'bg_color': '#1a1a24', 'font_color': '#7c6af7', 'border': 1})
        for ci, col in enumerate(df.columns):
            ws.write(0, ci, col, header_fmt)
            ws.set_column(ci, ci, max(12, len(str(col)) + 4))
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── Brand + user info ────────────────────────────────────────────────────
    owner   = st.session_state.get("bx360_key_owner", "User")
    plan    = st.session_state.get("key_plan", "—")
    credits = st.session_state.get("bx360_credits", 0)
    is_trial = st.session_state.get("bx360_is_free_trial", False)
    cred_color = "#3ecfcf" if (is_trial or credits > 10) else ("#f7a86a" if credits > 3 else "#f76a6a")
    cred_display = "∞" if is_trial else str(credits)
    cred_bar_w   = "100" if is_trial else str(min(100, credits))
    cred_label   = "Free Trial" if is_trial else "Credits remaining"

    st.html(f"""
    <div class="brand-header">
        <div class="brand-logo"></div>
        <div>
            <div class="brand-name">DataSynthX</div>
            <div class="brand-tag">Synthetic Data Platform</div>
        </div>
    </div>
    <div style="background:#0f0f18;border:1px solid #2a2a3a;border-radius:10px;
                padding:12px 14px;margin-bottom:20px;">
        <div style="font-family:Space Mono,monospace;font-size:9px;color:#6b6b80;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">Account</div>
        <div style="font-family:Syne,sans-serif;font-size:13px;font-weight:700;
                    color:#e8e8f0;margin-bottom:2px;">{owner}</div>
        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                    margin-bottom:10px;">{plan} plan</div>
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;">
                {cred_label}
            </div>
            <div style="font-family:Syne,sans-serif;font-size:20px;font-weight:800;
                        color:{cred_color};">{cred_display}</div>
        </div>
        <div style="background:#1a1a24;border-radius:4px;height:4px;margin-top:6px;overflow:hidden;">
            <div style="background:{cred_color};height:4px;width:{cred_bar_w}%;
                        border-radius:4px;transition:width 0.4s;"></div>
        </div>
    </div>
    """)

    if st.button("↩ Sign Out", use_container_width=True):
        from utils.auth import logout
        logout(extra_keys=["synth_df","trust_metrics","gen_status","ai_explanation",
                           "ai_use_case_saved","uploaded_file_bytes","uploaded_file_name"])
        st.rerun()

    if st.button("↺ Reset Analysis", use_container_width=True, key="reset_analysis_btn"):
        for k in ["synth_df","trust_metrics","gen_status","ai_explanation","ai_use_case_saved",
                  "uploaded_file_bytes","uploaded_file_name"]:
            st.session_state.pop(k, None)
        st.rerun()

    st.html('<div class="section-title">⬆ Upload Dataset</div>')
    uploaded_file = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )

    # Immediately read bytes into session state so reruns never lose the file
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        if file_bytes:  # guard against empty reads on slow reruns
            st.session_state["uploaded_file_bytes"] = file_bytes
            st.session_state["uploaded_file_name"] = uploaded_file.name

    st.markdown("---")
    st.html('<div class="section-title">⚙ Generation Config</div>')

    n_rows = st.number_input(
        "Target rows to generate",
        min_value=10,
        max_value=1_000_000,
        value=1000,
        step=100,
        help="Number of synthetic rows to generate"
    )

    noise_level = st.slider(
        "Noise level",
        min_value=0.0,
        max_value=0.20,
        value=0.02,
        step=0.01,
        help="Gaussian noise added to numeric columns (fraction of std)"
    )

    st.markdown("---")
    generate_btn = st.button("⬡ Generate Synthetic Data", type="primary")

    # ── Persistent generation status label ──────────────────────────────────
    gen_status = st.session_state.get("gen_status")
    if gen_status == "done":
        sci_val = st.session_state.get("trust_metrics", {}).get("sci", "—")
        n_synth = len(st.session_state.get("synth_df", []))
        st.html(
            f'<div style="background:rgba(62,207,207,0.08);border:1px solid rgba(62,207,207,0.25);'
            f'border-radius:8px;padding:10px 12px;margin-top:8px;">'
            f'<div style="font-family:Space Mono,monospace;font-size:10px;color:#3ecfcf;'
            f'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;">✓ Generation Complete</div>'
            f'<div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;line-height:1.7;">'
            f'{n_synth:,} rows generated<br>SCI Score: <span style="color:#3ecfcf;font-weight:700;">'
            f'{sci_val}/100</span></div></div>',
        )
    elif gen_status == "error":
        st.html(
            '<div style="background:rgba(247,106,106,0.08);border:1px solid rgba(247,106,106,0.25);'
            'border-radius:8px;padding:10px 12px;margin-top:8px;">'
            '<div style="font-family:Space Mono,monospace;font-size:10px;color:#f76a6a;'
            'letter-spacing:1.5px;text-transform:uppercase;">✗ Generation Failed</div>'
            '<div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;margin-top:4px;">'
            'Check your dataset and retry.</div></div>',
        )

    st.markdown("---")
    st.html("""
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#3a3a4a;letter-spacing:1px;text-transform:uppercase;line-height:2;">
        v1.0.0 · DataSynthX<br>
        Multivariate Gaussian<br>
        Freq-Preserving Sampling<br>
        KS · Wasserstein · KL
    </div>
    """)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

# Hero header
st.html("""
<div style="padding: 40px 0 24px;">
    <div style="font-family:Space Mono,monospace;font-size:10px;color:#3ecfcf;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
        AI-POWERED · STATISTICAL FIDELITY · PRODUCTION READY
    </div>
    <h1 style="font-family:Syne,sans-serif;font-size:42px;font-weight:800;margin:0;line-height:1.1;
               background:linear-gradient(90deg,#e8e8f0,#7c6af7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        Synthetic Data<br>Generation Platform
    </h1>
    <p style="color:#6b6b80;font-size:15px;margin-top:12px;font-family:Syne,sans-serif;">
        Upload your dataset → Learn its structure → Generate privacy-safe synthetic data at any scale
    </p>
</div>
""")

# Use session state bytes if the live file object is None (rerun/delay)
_has_file = (
    uploaded_file is not None or
    "uploaded_file_bytes" in st.session_state
)

if not _has_file:
    # Empty state
    st.html("""
    <div style="border:2px dashed #2a2a3a;border-radius:16px;padding:60px;text-align:center;margin-top:20px;">
        <div style="font-size:48px;margin-bottom:16px;">⬡</div>
        <div style="font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
            No Dataset Loaded
        </div>
        <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;line-height:1.8;">
            Upload a CSV or Excel file in the sidebar to begin.<br>
            DataSynthX will profile your data and generate<br>
            statistically faithful synthetic records at any scale.
        </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:32px;">
        <div class="metric-card">
            <div class="metric-label">Step 01</div>
            <div style="font-size:20px;font-weight:700;color:#7c6af7;margin:8px 0;">Upload & Profile</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                Auto-detects numeric, categorical & datetime columns. Computes distributions, correlations and missing value ratios.
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Step 02</div>
            <div style="font-size:20px;font-weight:700;color:#3ecfcf;margin:8px 0;">Generate at Scale</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                Multivariate Gaussian synthesis preserves correlations. Frequency-weighted categorical sampling. Up to 1M rows.
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Step 03</div>
            <div style="font-size:20px;font-weight:700;color:#f76a6a;margin:8px 0;">Trust Metrics</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;">
                KS-test, Wasserstein distance, KL divergence and a composite Structural Consistency Index (SCI) 0–100.
            </div>
        </div>
    </div>
    """)
    st.stop()


# ─── Load Data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes: bytes, file_name: str):
    name = file_name.lower()
    buffer = io.BytesIO(file_bytes)
    if name.endswith('.csv'):
        try:
            return pd.read_csv(buffer)
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(file_bytes), encoding='latin-1')
    elif name.endswith('.xlsx'):
        return pd.read_excel(buffer, engine='openpyxl')
    elif name.endswith('.xls'):
        return pd.read_excel(buffer, engine='xlrd')
    else:
        raise ValueError(f"Unsupported file type: {file_name}")

# Resolve file bytes — prefer live upload, fall back to session state
try:
    if uploaded_file is not None:
        _file_bytes = uploaded_file.read()
        if _file_bytes:
            st.session_state["uploaded_file_bytes"] = _file_bytes
            st.session_state["uploaded_file_name"] = uploaded_file.name
    _file_bytes = st.session_state.get("uploaded_file_bytes")
    _file_name  = st.session_state.get("uploaded_file_name", "upload")
    if not _file_bytes:
        st.error("Could not read the uploaded file. Please try uploading again.")
        st.stop()
    df = load_data(_file_bytes, _file_name)
except Exception as e:
    st.error(f"Failed to load file: {e}")
    st.stop()

# ─── Profile ────────────────────────────────────────────────────────────────
profiler = DataProfiler(df)
profile = profiler.profile()

numeric_cols = profile['numeric_cols']
categorical_cols = profile['categorical_cols']
datetime_cols = profile['datetime_cols']

# ─── Quick Stats Row ────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
cols_data = [
    (c1, str(df.shape[0]), "Original Rows", "#7c6af7"),
    (c2, str(df.shape[1]), "Total Columns", "#3ecfcf"),
    (c3, str(len(numeric_cols)), "Numeric Cols", "#7c6af7"),
    (c4, str(len(categorical_cols)), "Categorical Cols", "#3ecfcf"),
    (c5, f"{df.isna().mean().mean()*100:.1f}%", "Missing Rate", "#f76a6a"),
]
for col, val, label, color in cols_data:
    with col:
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
        </div>""")

st.html("<br>")

# ═══════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs(["📊  Data Profile", "🧬  Synthetic Data", "📐  Trust Metrics", "⬇  Export"])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1: DATA PROFILE
# ──────────────────────────────────────────────────────────────────────────
with tab1:
    st.html('<div class="section-title">Original Dataset Preview</div>')
    st.html('<div class="section-sub">First 100 rows of uploaded data</div>')
    st.dataframe(df.head(100),  width='stretch', height=240)

    if numeric_cols:
        st.html("<br>")
        st.html('<div class="section-title">Numeric Column Statistics</div>')
        stats_rows = []
        for col in numeric_cols:
            s = profile['numeric_stats'][col]
            stats_rows.append({
                'Column': col,
                'Mean': f"{s['mean']:.4f}",
                'Std Dev': f"{s['std']:.4f}",
                'Min': f"{s['min']:.4f}",
                'Max': f"{s['max']:.4f}",
                'Skewness': f"{s['skew']:.4f}",
                'Kurtosis': f"{s['kurtosis']:.4f}",
                'Missing %': f"{s['missing_ratio']*100:.1f}%"
            })
        st.dataframe(pd.DataFrame(stats_rows), width='stretch', hide_index=True)

    if categorical_cols:
        st.html("<br>")
        st.html('<div class="section-title">Categorical Column Summary</div>')
        cat_rows = []
        for col in categorical_cols:
            s = profile['categorical_stats'][col]
            top = sorted(s['frequencies'].items(), key=lambda x: -x[1])[:3]
            cat_rows.append({
                'Column': col,
                'Unique Values': s['n_unique'],
                'Mode': s['mode'],
                'Top 3 Categories': ', '.join([f"{k} ({v*100:.1f}%)" for k, v in top]),
                'Missing %': f"{s['missing_ratio']*100:.1f}%"
            })
        st.dataframe(pd.DataFrame(cat_rows), width='stretch', hide_index=True)

    if not profile['correlation_matrix'].empty:
        st.html("<br>")
        st.html('<div class="section-title">Correlation Matrix</div>')
        render_heatmap(profile['correlation_matrix'], "ORIGINAL DATA — PEARSON CORRELATION")

    # Distribution histograms
    if numeric_cols:
        st.html("<br>")
        st.html('<div class="section-title">Distribution Histograms</div>')
        cols_per_row = 3
        for i in range(0, len(numeric_cols), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col in enumerate(numeric_cols[i:i+cols_per_row]):
                with row_cols[j]:
                    vals = df[col].dropna()
                    fig = go.Figure(go.Histogram(
                        x=vals,
                        nbinsx=30,
                        marker=dict(
                            color="#7c6af7",
                            opacity=0.85,
                            line=dict(width=0),
                        ),
                        hovertemplate="%{x}<br>Count: %{y}<extra></extra>",
                    ))
                    fig.update_layout(
                        title=dict(text=col, font=dict(size=10, color="#6b6b80",
                                   family="Space Mono, monospace"), x=0),
                        paper_bgcolor="#111118", plot_bgcolor="#111118",
                        margin=dict(l=4, r=4, t=28, b=4),
                        height=150,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True,
                                   tickfont=dict(size=8, color="#6b6b80")),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        bargap=0.05,
                    )
                    st.plotly_chart(fig, use_container_width=True,
                                   config={"displayModeBar": False})

# ──────────────────────────────────────────────────────────────────────────
# TAB 2: SYNTHETIC DATA
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    if 'synth_df' not in st.session_state:
        st.html("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">🧬</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                Ready to Generate
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Configure settings in the sidebar and click<br><strong style="color:#7c6af7">Generate Synthetic Data</strong>
            </div>
        </div>""")
    else:
        synth_df = st.session_state['synth_df']
        st.html('<div class="section-title">Synthetic Dataset Preview</div>')
        st.html(f'<div class="section-sub">{len(synth_df):,} rows generated · {synth_df.shape[1]} columns</div>')
        st.dataframe(synth_df.head(100), width='stretch', height=280)

        # Side-by-side summary
        st.html("<br>")
        st.html('<div class="section-title">Original vs Synthetic — Summary Comparison</div>')

        if numeric_cols:
            compare_rows = []
            for col in numeric_cols:
                o = df[col].dropna()
                s = synth_df[col].dropna()
                compare_rows.append({
                    'Column': col,
                    'Orig Mean': f"{o.mean():.4f}",
                    'Synth Mean': f"{s.mean():.4f}",
                    'Orig Std': f"{o.std():.4f}",
                    'Synth Std': f"{s.std():.4f}",
                    'Orig Min': f"{o.min():.4f}",
                    'Synth Min': f"{s.min():.4f}",
                    'Orig Max': f"{o.max():.4f}",
                    'Synth Max': f"{s.max():.4f}",
                })
            st.dataframe(pd.DataFrame(compare_rows), width='stretch', hide_index=True)

        # Overlay histograms
        if numeric_cols:
            st.html("<br>")
            st.html('<div class="section-title">Distribution Overlay — Original vs Synthetic</div>')
            cols_per_row = 3
            for i in range(0, len(numeric_cols), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, col in enumerate(numeric_cols[i:i+cols_per_row]):
                    with row_cols[j]:
                        o_vals = df[col].dropna()
                        s_vals = synth_df[col].dropna()
                        fig = go.Figure()
                        fig.add_trace(go.Histogram(
                            x=o_vals, name="Original", nbinsx=30,
                            marker=dict(color="#7c6af7", opacity=0.7, line=dict(width=0)),
                            hovertemplate="Original<br>%{x}<br>Count: %{y}<extra></extra>",
                        ))
                        fig.add_trace(go.Histogram(
                            x=s_vals, name="Synthetic", nbinsx=30,
                            marker=dict(color="#3ecfcf", opacity=0.5, line=dict(width=0)),
                            hovertemplate="Synthetic<br>%{x}<br>Count: %{y}<extra></extra>",
                        ))
                        fig.update_layout(
                            barmode="overlay",
                            title=dict(text=col, font=dict(size=10, color="#6b6b80",
                                       family="Space Mono, monospace"), x=0),
                            paper_bgcolor="#111118", plot_bgcolor="#111118",
                            margin=dict(l=4, r=4, t=28, b=4),
                            height=160,
                            xaxis=dict(showgrid=False, zeroline=False,
                                       tickfont=dict(size=8, color="#6b6b80")),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            legend=dict(
                                orientation="h", x=0, y=1.15,
                                font=dict(size=9, color="#9999b0"),
                                bgcolor="rgba(0,0,0,0)",
                            ),
                            bargap=0.05,
                        )
                        st.plotly_chart(fig, width='stretch',
                                       config={"displayModeBar": False})


# ──────────────────────────────────────────────────────────────────────────
# TAB 3: TRUST METRICS
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    if 'trust_metrics' not in st.session_state:
        st.html("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">📐</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                Awaiting Generation
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Generate synthetic data first to see trust metrics.
            </div>
        </div>""")
    else:
        tm = st.session_state['trust_metrics']
        sci = tm['sci']
        color = score_color(sci)
        badge_cls, badge_label = score_badge(sci)

        # SCI Hero
        pct = sci / 100
        circumference = 2 * 3.14159 * 54
        dash = circumference * pct
        gap = circumference - dash

        st.html(f"""
        <div class="sci-container" style="margin-bottom:24px;">
            <div class="metric-label" style="margin-bottom:16px;">STRUCTURAL CONSISTENCY INDEX</div>
            <svg width="160" height="160" viewBox="0 0 120 120" style="display:block;margin:0 auto 12px;">
                <circle cx="60" cy="60" r="54" fill="none" stroke="#1a1a24" stroke-width="10"/>
                <circle cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="10"
                    stroke-dasharray="{dash:.1f} {gap:.1f}"
                    stroke-dashoffset="{circumference/4:.1f}"
                    stroke-linecap="round"/>
                <text x="60" y="56" text-anchor="middle" font-size="28" font-weight="800"
                      fill="{color}" font-family="Syne,sans-serif">{sci}</text>
                <text x="60" y="72" text-anchor="middle" font-size="10"
                      fill="#6b6b80" font-family="Space Mono,monospace">/ 100</text>
            </svg>
            <div style="font-size:48px;font-weight:800;color:{color};line-height:1;margin-bottom:4px;">{sci}</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;margin-bottom:10px;">/ 100</div>
            <span class="badge {badge_cls}">{badge_label}</span>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;margin-top:12px;">
                Weighted composite of correlation, distribution and categorical fidelity scores
            </div>
        </div>
        """)

        # Sub-scores
        c1, c2, c3 = st.columns(3)
        sub_scores = [
            (c1, "Correlation Preservation", tm['correlation_score'], "30% weight · Pearson matrix comparison"),
            (c2, "Distribution Similarity", tm['distribution_score'], "40% weight · KS-test · Wasserstein"),
            (c3, "Categorical Fidelity", tm['categorical_score'], "30% weight · KL Divergence"),
        ]
        for col, label, score, note in sub_scores:
            with col:
                clr = score_color(score)
                st.html(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{clr}">{score}</div>
                    <div class="metric-sub">{note}</div>
                </div>""")

        # Correlation heatmaps
        if not tm['orig_corr'].empty:
            st.html("<br>")
            st.html('<div class="section-title">Correlation Matrix Comparison</div>')
            col_a, col_b = st.columns(2)
            with col_a:
                render_heatmap(tm['orig_corr'], "ORIGINAL DATA")
            with col_b:
                render_heatmap(tm['synth_corr'], "SYNTHETIC DATA")

        # Distribution scores table
        if tm['dist_scores']:
            st.html("<br>")
            st.html('<div class="section-title">Per-Column Distribution Metrics</div>')
            dist_rows = []
            for col_name, v in tm['dist_scores'].items():
                badge_c, badge_t = score_badge(v['score'] * 100)
                dist_rows.append({
                    'Column': col_name,
                    'KS Statistic': f"{v['ks_stat']:.4f}",
                    'KS p-value': f"{v['ks_pvalue']:.4f}",
                    'Wasserstein (norm.)': f"{v['wasserstein']:.4f}",
                    'Fidelity Score': f"{v['score']*100:.1f}",
                    'Status': badge_t
                })
            st.dataframe(pd.DataFrame(dist_rows), width='stretch', hide_index=True)

        # Categorical fidelity
        if tm['cat_scores']:
            st.html("<br>")
            st.html('<div class="section-title">Categorical Distribution Fidelity</div>')
            cat_rows = []
            for col_name, v in tm['cat_scores'].items():
                badge_c, badge_t = score_badge(v['score'] * 100)
                cat_rows.append({
                    'Column': col_name,
                    'KL Divergence': f"{v['kl_divergence']:.4f}",
                    'Fidelity Score': f"{v['score']*100:.1f}",
                    'Status': badge_t
                })
            st.dataframe(pd.DataFrame(cat_rows), width='stretch', hide_index=True)

        # ── AI Explainer ──────────────────────────────────────────────────
        st.html("<br>")
        st.html("""
        <div style="border-top:1px solid #2a2a3a;padding-top:28px;margin-top:8px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <div style="width:8px;height:8px;border-radius:50%;
                            background:linear-gradient(135deg,#7c6af7,#3ecfcf);"></div>
                <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                            letter-spacing:2px;text-transform:uppercase;">AI Analysis</div>
            </div>
            <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;
                        color:#e8e8f0;margin-bottom:4px;">Understand your results</div>
            <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;
                        line-height:1.7;margin-bottom:20px;">
                Tell the AI what you're building and it'll interpret your metrics in plain language —
                flagging what's working, what to watch, and whether your data is fit for purpose.
                Uses 1 credit.
            </div>
        </div>
        """)

        if st.session_state.get("bx360_is_free_trial", False):
            # ── Free trial block ─────────────────────────────────────────────
            st.html("""
            <div style="background:linear-gradient(135deg,rgba(124,106,247,0.07),rgba(62,207,207,0.05));
                        border:1px solid rgba(124,106,247,0.28);border-left:3px solid #7c6af7;
                        border-radius:12px;padding:24px 26px;margin-bottom:8px;">
                <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:800;
                            color:#a89df5;margin-bottom:8px;">✦ AI Explainer · Paid Feature</div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#9999b0;
                            line-height:1.85;margin-bottom:18px;">
                    AI-powered quality analysis is <span style="color:#e8e8f0;font-weight:700;">not available on the Free Trial</span>.
                    Upgrade to any paid plan to unlock:<br><br>
                    &nbsp;&nbsp;✓&nbsp; Plain-language interpretation of your SCI score and per-column metrics<br>
                    &nbsp;&nbsp;✓&nbsp; Use-case fit assessment for your specific project<br>
                    &nbsp;&nbsp;✓&nbsp; Actionable suggestions on noise level, row count &amp; column quality
                </div>
            </div>
            """)
            _, upg_col, _ = st.columns([1, 2, 1])
            with upg_col:
                st.link_button("⬡ Upgrade to Paid Plan →", "https://x.com/bayantx360",
                               use_container_width=True)
        else:
            use_case_input = st.text_area(
                "What are you using this synthetic data for?",
                placeholder="e.g. conducting thesis/dissertation analysis; training a churn prediction model, anonymising patient records for research,...",
                height=80,
                key="ai_use_case_input",
                label_visibility="visible",
            )

            explain_btn = st.button(
                "✦ Analyse Data Quality and Use case fit",
                key="explain_btn",
                width='stretch',
            )

            if explain_btn:
                current_credits = st.session_state.get("bx360_credits", 0)
                if current_credits <= 0:
                    st.error("No credits remaining. Please purchase a plan to continue.")
                else:
                    # Build a rich but compact context dict for the prompt
                    dist_summary = {
                        col: {
                            "ks_stat": round(v["ks_stat"], 4),
                            "wasserstein_norm": round(v["wasserstein"], 4),
                            "fidelity_score": round(v["score"] * 100, 1),
                        }
                        for col, v in tm["dist_scores"].items()
                    } if tm["dist_scores"] else {}

                    cat_summary = {
                        col: {
                            "kl_divergence": round(v["kl_divergence"], 4),
                            "fidelity_score": round(v["score"] * 100, 1),
                        }
                        for col, v in tm["cat_scores"].items()
                    } if tm["cat_scores"] else {}

                    # Column names give the AI crucial domain context
                    all_columns = list(df.columns)
                    n_orig      = len(df)
                    n_synth     = len(st.session_state["synth_df"])

                    use_case = use_case_input.strip() if use_case_input.strip() else None

                    system_prompt = """You are a data scientist reviewing synthetic data quality results for a user.
Your job is to give a plain, honest, peer-level interpretation of the metrics — not a tutorial.
Write 3–4 short paragraphs. No bullet points, no headers, no metric definitions.
Start by inferring what the dataset is likely for based on the column names, then immediately confirm or adjust based on the user's stated use case if provided.
Name specific columns when they are notably good or bad. Be direct about whether the data is fit for its purpose.
End with one concrete, actionable suggestion — row count, noise level, or a specific column to watch.
Tone: like a colleague who just looked over your shoulder at the results."""

                    user_message = f"""Dataset columns: {all_columns}
Original rows: {n_orig} → Synthetic rows: {n_synth}
SCI Score: {tm['sci']}/100
Correlation preservation: {tm['correlation_score']}/100
Distribution similarity: {tm['distribution_score']}/100
Categorical fidelity: {tm['categorical_score']}/100
Per-column distribution scores: {dist_summary}
Per-column categorical scores: {cat_summary}
{"User's stated use case: " + use_case if use_case else "No use case stated — infer from column names."}"""

                    with st.spinner("Analysing synthetic data quality and use case fit…"):
                        try:
                            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user",   "content": user_message},
                                ],
                                temperature=0.5,
                                max_tokens=600,
                            )
                            explanation = response.choices[0].message.content.strip()

                            # Deduct 1 credit for the AI run
                            new_balance = spend_credits("datasynthx")
                            # credits synced by spend_credits()

                            st.session_state["ai_explanation"]  = explanation
                            st.session_state["ai_use_case_saved"] = use_case or "inferred from columns"

                        except Exception as e:
                            st.error(f"AI analysis failed: {e}")

        # Render stored explanation (persists across reruns)
        if st.session_state.get("ai_explanation"):
            explanation = st.session_state["ai_explanation"]
            stated_use  = st.session_state.get("ai_use_case_saved", "")
            credits_left = st.session_state.get("bx360_credits", 0)
            cred_color   = "#3ecfcf" if credits_left > 10 else ("#f7a86a" if credits_left > 3 else "#f76a6a")

            # Escape for HTML embedding
            html_text = explanation.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n\n", "</p><p style='margin:0 0 14px 0;'>").replace("\n", " ")

            st.html(f"""
            <div style="background:linear-gradient(135deg,rgba(124,106,247,0.06),rgba(62,207,207,0.04));
                        border:1px solid rgba(124,106,247,0.2);border-radius:14px;
                        padding:24px 28px;margin-top:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="width:6px;height:6px;border-radius:50%;background:#7c6af7;"></div>
                        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                    letter-spacing:2px;text-transform:uppercase;">AI Analysis</div>
                    </div>
                    <div style="font-family:Space Mono,monospace;font-size:10px;color:{cred_color};">
                        {credits_left} credits remaining
                    </div>
                </div>
                {"" if not stated_use or stated_use == "inferred from columns" else
                 f'<div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;'
                 f'background:rgba(124,106,247,0.08);border-radius:6px;padding:6px 10px;'
                 f'margin-bottom:16px;border-left:2px solid #7c6af7;">Use case: {stated_use}</div>'
                }
                <div style="font-family:Syne,sans-serif;font-size:14px;color:#c8c8d8;line-height:1.8;">
                    <p style="margin:0 0 14px 0;">{html_text}</p>
                </div>
            </div>
            """)


# ──────────────────────────────────────────────────────────────────────────
# TAB 4: EXPORT
# ──────────────────────────────────────────────────────────────────────────
with tab4:
    if 'synth_df' not in st.session_state:
        st.html("""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:40px;margin-bottom:12px;">⬇</div>
            <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#e8e8f0;margin-bottom:8px;">
                No Data to Export
            </div>
            <div style="font-family:Space Mono,monospace;font-size:12px;color:#6b6b80;">
                Generate synthetic data first.
            </div>
        </div>""")
    else:
        synth_df = st.session_state['synth_df']
        st.html('<div class="section-title">⬇ Export Synthetic Dataset</div>')
        st.html(f'<div class="section-sub">{len(synth_df):,} rows ready for download</div>')

        # Summary card
        sci_val = st.session_state.get('trust_metrics', {}).get('sci', 'N/A')
        clr = score_color(float(sci_val)) if isinstance(sci_val, (int, float)) else '#7c6af7'

        st.html(f"""
        <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:24px;margin-bottom:24px;
                    display:grid;grid-template-columns:repeat(4,1fr);gap:20px;">
            <div>
                <div class="metric-label">Rows Generated</div>
                <div style="font-size:24px;font-weight:800;color:#7c6af7;">{len(synth_df):,}</div>
            </div>
            <div>
                <div class="metric-label">Columns</div>
                <div style="font-size:24px;font-weight:800;color:#3ecfcf;">{synth_df.shape[1]}</div>
            </div>
            <div>
                <div class="metric-label">SCI Score</div>
                <div style="font-size:24px;font-weight:800;color:{clr};">{sci_val}</div>
            </div>
            <div>
                <div class="metric-label">Memory (approx)</div>
                <div style="font-size:24px;font-weight:800;color:#e8e8f0;">{synth_df.memory_usage(deep=True).sum()//1024:,} KB</div>
            </div>
        </div>
        """)

        # ── Download credit cost info ─────────────────────────────────────────
        is_trial      = st.session_state.get("bx360_is_free_trial", False)
        n_synth_rows  = len(synth_df)
        dl_cost       = download_credit_cost(n_synth_rows)
        current_creds = st.session_state.get("bx360_credits", 0)

        if is_trial:
            if n_synth_rows > 70:
                cost_label = "Upgrade required — Free Trial limited to 70 rows"
                cost_color = "#f76a6a"
            else:
                cost_label = "Free Trial · ≤70 rows · No credit needed"
                cost_color = "#3ecfcf"
        else:
            if dl_cost == 0:
                cost_label = "Download cost: Free (under 100 rows)"
                cost_color = "#3ecfcf"
            else:
                tier = ("100–500 rows → 1 credit" if n_synth_rows <= 500
                        else "501–1,000 rows → 2 credits" if n_synth_rows <= 1000
                        else "1,000+ rows → 5 credits")
                cost_label = f"Download cost: {dl_cost} credit{'s' if dl_cost != 1 else ''} · {tier}"
                cost_color = "#f7a86a" if current_creds < dl_cost else "#7c6af7"

        st.html(f"""
        <div style="background:rgba(124,106,247,0.06);border:1px solid rgba(124,106,247,0.2);
                    border-radius:10px;padding:12px 16px;margin-bottom:16px;
                    font-family:Space Mono,monospace;font-size:11px;color:{cost_color};">
            ⬡ {cost_label}
        </div>
        """)

        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            st.html("""
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:20px;margin-bottom:12px;">
                <div class="metric-label" style="margin-bottom:8px;">CSV Export</div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;margin-bottom:12px;">
                    Universal format · UTF-8 encoded<br>Compatible with all data tools
                </div>
            </div>""")

            if is_trial and n_synth_rows > 70:
                st.html(f"""
                <div style="background:rgba(124,106,247,0.07);border:1px solid rgba(124,106,247,0.25);
                            border-radius:10px;padding:16px 18px;margin-bottom:10px;
                            font-family:Space Mono,monospace;font-size:11px;
                            color:#9999b0;line-height:1.8;">
                    <div style="font-family:Syne,sans-serif;font-weight:700;font-size:13px;
                                color:#a89df5;margin-bottom:6px;">⬡ Paid Feature</div>
                    Your dataset has <span style="color:#e8e8f0;font-weight:700;">{n_synth_rows:,} rows</span>.
                    CSV export is limited to <strong style="color:#e8e8f0;">70 rows</strong> on the Free Trial.
                    Upgrade to download the full dataset.
                </div>
                """)
                st.link_button("Upgrade — Get Access Key →", "https://x.com/bayantx360",
                               use_container_width=True)
            elif not is_trial and dl_cost > 0 and current_creds < dl_cost:
                st.html(f"""
                <div style="background:rgba(247,106,106,0.08);border:1px solid rgba(247,106,106,0.25);
                            border-radius:10px;padding:14px 16px;margin-bottom:10px;
                            font-family:Space Mono,monospace;font-size:11px;color:#f76a6a;">
                    Insufficient credits. This download costs {dl_cost} credit{'s' if dl_cost != 1 else ''}
                    but you have {current_creds}. Please top up your plan.
                </div>
                """)
                st.link_button("Get More Credits →", "https://x.com/bayantx360",
                               use_container_width=True)
            else:
                csv_data = synth_df.to_csv(index=False).encode('utf-8')
                if st.download_button(
                    "⬇ Download CSV",
                    data=csv_data,
                    file_name="datasynthx_synthetic.csv",
                    mime="text/csv",
                    key="csv_dl_btn"
                ):
                    if not is_trial and dl_cost > 0:
                        new_bal = spend_credits("datasynthx", dl_cost)
                        # credits synced by spend_credits()
                        st.toast(f"✓ {dl_cost} credit{'s' if dl_cost != 1 else ''} deducted · {new_bal} remaining", icon="✅")
                        st.rerun()
                if is_trial:
                    st.html("""
                    <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                margin-top:6px;">Free Trial · ≤70 rows included</div>
                    """)
                elif dl_cost == 0:
                    st.html("""
                    <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                margin-top:6px;">No credit deducted · under 100 rows</div>
                    """)
                else:
                    st.html(f"""
                    <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                margin-top:6px;">{dl_cost} credit{'s' if dl_cost != 1 else ''} deducted on download</div>
                    """)

        with col_dl2:
            st.html("""
            <div style="background:#111118;border:1px solid #2a2a3a;border-radius:12px;padding:20px;margin-bottom:12px;">
                <div class="metric-label" style="margin-bottom:8px;">Excel Export</div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;line-height:1.7;margin-bottom:12px;">
                    Styled .xlsx format · Column widths<br>auto-fitted · Purple header theme
                </div>
            </div>""")

            if is_trial and n_synth_rows > 70:
                st.html(f"""
                <div style="background:rgba(124,106,247,0.07);border:1px solid rgba(124,106,247,0.25);
                            border-radius:10px;padding:16px 18px;margin-bottom:10px;
                            font-family:Space Mono,monospace;font-size:11px;
                            color:#9999b0;line-height:1.8;">
                    <div style="font-family:Syne,sans-serif;font-weight:700;font-size:13px;
                                color:#a89df5;margin-bottom:6px;">⬡ Paid Feature</div>
                    Your dataset has <span style="color:#e8e8f0;font-weight:700;">{n_synth_rows:,} rows</span>.
                    Excel export is limited to <strong style="color:#e8e8f0;">70 rows</strong> on the Free Trial.
                    Upgrade to download the full dataset as a styled .xlsx file.
                </div>
                """)
                st.link_button("Upgrade — Get Access Key →", "https://x.com/bayantx360",
                               use_container_width=True)
            elif not is_trial and dl_cost > 0 and current_creds < dl_cost:
                st.html(f"""
                <div style="background:rgba(247,106,106,0.08);border:1px solid rgba(247,106,106,0.25);
                            border-radius:10px;padding:14px 16px;margin-bottom:10px;
                            font-family:Space Mono,monospace;font-size:11px;color:#f76a6a;">
                    Insufficient credits. This download costs {dl_cost} credit{'s' if dl_cost != 1 else ''}
                    but you have {current_creds}. Please top up your plan.
                </div>
                """)
                st.link_button("Get More Credits →", "https://x.com/bayantx360",
                               use_container_width=True)
            else:
                try:
                    excel_data = to_excel_bytes(synth_df)
                    if st.download_button(
                        "⬇ Download Excel",
                        data=excel_data,
                        file_name="datasynthx_synthetic.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="xlsx_dl_btn"
                    ):
                        if not is_trial and dl_cost > 0:
                            new_bal = spend_credits("datasynthx", dl_cost)
                            # credits synced by spend_credits()
                            st.toast(f"✓ {dl_cost} credit{'s' if dl_cost != 1 else ''} deducted · {new_bal} remaining", icon="✅")
                            st.rerun()
                    if is_trial:
                        st.html("""
                        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                    margin-top:6px;">Free Trial · ≤70 rows included</div>
                        """)
                    elif dl_cost == 0:
                        st.html("""
                        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                    margin-top:6px;">No credit deducted · under 100 rows</div>
                        """)
                    else:
                        st.html(f"""
                        <div style="font-family:Space Mono,monospace;font-size:10px;color:#6b6b80;
                                    margin-top:6px;">{dl_cost} credit{'s' if dl_cost != 1 else ''} deducted on download</div>
                        """)
                except Exception as e:
                    st.warning(f"Excel export unavailable: {e}. Use CSV instead.")


# ═══════════════════════════════════════════════════════════════════════════
#  GENERATION TRIGGER
# ═══════════════════════════════════════════════════════════════════════════

if generate_btn:
    # ── Free trial row cap ───────────────────────────────────────────────────
    if st.session_state.get("bx360_is_free_trial", False) and n_rows > 70:
        st.error(
            "⬡ Free Trial is limited to 70 rows per generation. "
            "Please reduce your row count or upgrade to a paid plan."
        )
        st.stop()

    if not numeric_cols and not categorical_cols:
        st.session_state['gen_status'] = 'error'
        st.error("No usable columns found. Please check your dataset.")
    else:
        with st.spinner(""):
            try:
                progress_bar = st.progress(0, text="Initializing generator…")

                progress_bar.progress(15, text="Building statistical model…")
                generator = SyntheticDataGenerator(df, profile)

                progress_bar.progress(40, text=f"Generating {n_rows:,} synthetic rows…")
                synth_df = generator.generate(n_rows, noise_level=noise_level)

                progress_bar.progress(70, text="Computing trust metrics…")
                tm = TrustMetrics(df, synth_df, profile)
                trust_data = tm.compute_sci()

                # Generation is FREE for all users — no credit deducted here
                progress_bar.progress(90, text="Finalizing…")

                progress_bar.progress(95, text="Finalizing…")
                st.session_state['synth_df']      = synth_df
                st.session_state['trust_metrics'] = trust_data
                st.session_state['gen_status']    = 'done'
                # Clear any previous AI explanation so it doesn't show stale results
                st.session_state.pop('ai_explanation', None)
                st.session_state.pop('ai_use_case_saved', None)

                progress_bar.progress(100, text="Done!")
            except Exception as _gen_err:
                st.session_state['gen_status'] = 'error'
                st.error(f"Generation failed: {_gen_err}")
                st.rerun()

        sci = trust_data['sci']
        clr = score_color(sci)
        badge_cls, badge_label = score_badge(sci)
        remaining = st.session_state.get("bx360_credits", 0)
        remaining_display = "∞" if st.session_state.get("bx360_is_free_trial", False) else str(remaining)

        st.html(f"""
        <div style="background:linear-gradient(135deg,rgba(124,106,247,0.08),rgba(62,207,207,0.08));
                    border:1px solid rgba(124,106,247,0.3);border-radius:12px;
                    padding:20px 24px;margin-top:16px;display:flex;align-items:center;gap:16px;">
            <div style="font-size:32px;">✓</div>
            <div>
                <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#e8e8f0;">
                    {n_rows:,} synthetic rows generated successfully
                </div>
                <div style="font-family:Space Mono,monospace;font-size:11px;color:#6b6b80;margin-top:4px;">
                    SCI Score: <span style="color:{clr};font-weight:700;">{sci}/100</span> ·
                    Status: <span class="badge {badge_cls}">{badge_label}</span> ·
                    Credits left: <span style="color:#3ecfcf;font-weight:700;">{remaining_display}</span>
                </div>
            </div>
        </div>
        """)

        st.rerun()

"""
utils/styles.py
─────────────────────────────────────────────────────────────────────────────
Shared CSS injection and sidebar credit widget for the Bayantx360 ecosystem.
Each product can inject its own accent colour while the base chrome stays
consistent.
"""

from __future__ import annotations
import streamlit as st


# ── Base dark theme (product-neutral) ─────────────────────────────────────────
_BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=Fira+Code:wght@400;500&display=swap');

:root {{
  --bg:        #03050d;
  --surface:   #0b1225;
  --surface2:  #0f1a30;
  --border:    rgba(255,255,255,0.07);
  --text-1:    #f0f6ff;
  --text-2:    #8a9bbf;
  --text-3:    #4a5a78;
  --green:     #34d399;
  --red:       #f87171;
  --yellow:    #fbbf24;
  --accent:    {accent};
  --accent2:   {accent2};
  --font-display: 'Syne', sans-serif;
  --font-body:    'DM Sans', sans-serif;
  --font-mono:    'Fira Code', monospace;
}}

html, body, [class*="css"] {{
  font-family: var(--font-body);
  background-color: var(--bg);
  -webkit-font-smoothing: antialiased;
}}
.stApp {{ background: var(--bg); }}

[data-testid="stSidebar"] {{
  background: #060b18 !important;
  border-right: 1px solid var(--border);
}}

h1 {{ color: var(--accent)  !important; font-family: var(--font-display) !important; font-weight: 800 !important; }}
h2 {{ color: var(--accent2) !important; font-family: var(--font-display) !important; font-weight: 700 !important;
      border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
h3 {{ color: var(--text-1)  !important; font-family: var(--font-display) !important; font-weight: 600 !important; }}

/* Buttons */
.stButton > button {{
  background: linear-gradient(135deg, #151a2e, #1e2745) !important;
  border: 1px solid var(--accent) !important;
  color: var(--accent) !important;
  font-family: var(--font-display) !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
}}
.stButton > button:hover {{
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: var(--bg) !important;
  border-color: transparent !important;
}}
.stDownloadButton > button {{
  background: linear-gradient(135deg, #0f1f18, #122518) !important;
  border: 1px solid var(--green) !important;
  color: var(--green) !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
  background: var(--surface); border-radius: 10px;
  padding: 4px; gap: 4px; border: 1px solid var(--border);
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent; border-radius: 8px;
  color: var(--text-3); font-size: 13px; font-weight: 500;
  padding: 8px 18px; border: none;
}}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: white !important;
}}

/* Inputs */
.stTextInput input, .stNumberInput input {{
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text-1) !important;
}}

/* Utility classes */
.bx-info  {{ background: rgba(62,232,255,0.07); border: 1px solid rgba(62,232,255,0.2);
             border-radius: 8px; padding: 12px 16px; color: #c7d2fe;
             font-size: .88rem; margin: 8px 0; line-height: 1.6; }}
.bx-warn  {{ background: rgba(251,191,36,0.07); border: 1px solid rgba(251,191,36,0.25);
             border-radius: 8px; padding: 12px 16px; color: #fde68a;
             font-size: .88rem; margin: 8px 0; line-height: 1.6; }}
.bx-lock  {{ background: rgba(62,232,255,0.06); border: 1px solid rgba(62,232,255,0.2);
             border-left: 3px solid var(--accent); border-radius: 8px;
             padding: 18px 20px; margin: 8px 0; }}
.bx-metric-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 18px 20px; text-align: center;
  position: relative; overflow: hidden;
}}
.bx-metric-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
}}
.bx-metric-val   {{ font-size: 2rem; font-weight: 700; color: var(--accent); line-height: 1.1; font-family: var(--font-display); }}
.bx-metric-label {{ font-size: .7rem; color: var(--text-3); text-transform: uppercase;
                    letter-spacing: 1px; margin-top: 6px; font-weight: 500; }}
.bx-step-badge {{
  display: inline-flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg, var(--surface), var(--surface2));
  border: 1px solid var(--border); border-left: 3px solid var(--accent);
  padding: 11px 18px; border-radius: 8px; color: var(--text-1);
  font-size: .95rem; font-weight: 600; margin-bottom: 18px; width: 100%;
  font-family: var(--font-display);
}}
.bx-step-num {{
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: var(--bg); border-radius: 50%; width: 26px; height: 26px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 700; flex-shrink: 0;
}}
.bx-pill-pass {{ background: rgba(52,211,153,.12); color: var(--green);
                 border: 1px solid rgba(52,211,153,.4); border-radius: 20px;
                 padding: 3px 14px; font-size: .78rem; font-weight: 600; display: inline-block; }}
.bx-pill-fail {{ background: rgba(248,113,113,.12); color: var(--red);
                 border: 1px solid rgba(248,113,113,.4); border-radius: 20px;
                 padding: 3px 14px; font-size: .78rem; font-weight: 600; display: inline-block; }}
.bx-divider   {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}

code, pre {{ font-family: var(--font-mono) !important; }}
#MainMenu {{ visibility: hidden; }}
footer    {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}
</style>
"""


def inject_base_css(accent: str = "#3ee8ff", accent2: str = "#818cf8") -> None:
    """Inject the shared dark-theme CSS with product-specific accent colours."""
    st.markdown(_BASE_CSS.format(accent=accent, accent2=accent2), unsafe_allow_html=True)


# ── Sidebar credit widget ──────────────────────────────────────────────────────

def render_sidebar_credit_widget(
    product_label: str,
    product_icon:  str,
    accent:        str = "#3ee8ff",
) -> None:
    """
    Renders the standardised account/credit widget at the top of the sidebar.
    Call this inside a `with st.sidebar:` block.
    """
    from utils.auth import is_free_trial, current_credits

    trial    = is_free_trial()
    credits  = current_credits()
    owner    = st.session_state.get("bx360_key_owner", "User")

    if trial:
        cred_color   = "#fbbf24"
        cred_display = "Trial"
        cred_label   = "Free Trial · export locked"
        bar_pct      = "100"
    else:
        cred_color   = "#34d399" if credits > 10 else ("#fbbf24" if credits > 3 else "#f87171")
        cred_display = str(credits)
        cred_label   = "Credits remaining"
        bar_pct      = str(min(100, credits * 2))

    st.markdown(f"""
    <div style="padding:16px 0 20px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:20px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,{accent},{accent}aa);
                    border-radius:8px;display:flex;align-items:center;justify-content:center;
                    font-size:16px;flex-shrink:0;">{product_icon}</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;
                      background:linear-gradient(90deg,{accent},{accent}88);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{product_label}</div>
          <div style="font-family:'Fira Code',monospace;font-size:9px;color:#4a5a78;
                      letter-spacing:2px;text-transform:uppercase;font-weight:500;">Bayantx360</div>
        </div>
      </div>
      <div style="background:#03050d;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:12px 14px;">
        <div style="font-family:'Fira Code',monospace;font-size:9px;color:#4a5a78;
                    letter-spacing:2px;text-transform:uppercase;font-weight:500;margin-bottom:6px;">Account</div>
        <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:600;
                    color:#f0f6ff;margin-bottom:8px;">{owner}</div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
          <div style="font-size:10px;color:#4a5a78;">{cred_label}</div>
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;
                      color:{cred_color};">{cred_display}</div>
        </div>
        <div style="background:#0f1a30;border-radius:4px;height:3px;overflow:hidden;">
          <div style="background:{cred_color};height:3px;width:{bar_pct}%;border-radius:4px;
                      transition:width 0.4s;"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

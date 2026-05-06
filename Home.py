"""
Home.py — Bayantx360 Central Hub
─────────────────────────────────────────────────────────────────────────────
This is the entry point for the multipage Streamlit app.
It renders the Bayantx360 product landing page and lets users navigate
to any of the three tools: PanelStatX, DataSynthX, EFActor.

Run with:
    streamlit run Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="Bayantx360 — AI & Analytics Ecosystem",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Fira+Code:wght@400;500&display=swap');

:root {
  --bg:       #03050d;
  --surface:  #0b1225;
  --surface2: #0f1a30;
  --border:   rgba(255,255,255,0.07);
  --cyan:     #3ee8ff;
  --indigo:   #818cf8;
  --amber:    #fbbf24;
  --green:    #34d399;
  --text-1:   #f0f6ff;
  --text-2:   #8a9bbf;
  --text-3:   #4a5a78;
  --font-d:   'Syne', sans-serif;
  --font-b:   'DM Sans', sans-serif;
  --font-m:   'Fira Code', monospace;
}
html, body, [class*="css"] {
  font-family: var(--font-b);
  background-color: var(--bg);
  -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg); }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 1100px; margin: 0 auto; padding-top: 0 !important; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Nav bar ── */
.bx-nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(3,5,13,0.90);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 -6rem;           /* bleed past block-container */
}
.bx-logo {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--font-d); font-size: 20px; font-weight: 800;
  color: var(--text-1); letter-spacing: -.02em; text-decoration: none;
}
.bx-logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--cyan), #4f8fff);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
}
.bx-logo span { color: var(--cyan); }

/* ── Hero ── */
.bx-hero {
  text-align: center;
  padding: 88px 20px 64px;
  position: relative;
}
.bx-hero h1 {
  font-family: var(--font-d);
  font-size: clamp(36px, 6vw, 76px);
  font-weight: 800;
  line-height: 1.0;
  letter-spacing: -.03em;
  color: var(--text-1);
  margin-bottom: 24px;
}
.bx-grad {
  background: linear-gradient(95deg, var(--cyan) 0%, #4f8fff 50%, var(--indigo) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.bx-hero p {
  font-size: clamp(15px, 2vw, 18px);
  color: var(--text-2);
  max-width: 580px;
  margin: 0 auto 40px;
  line-height: 1.75;
  font-weight: 300;
}
.bx-tag {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 14px; border-radius: 100px;
  border: 1px solid rgba(62,232,255,0.25);
  background: rgba(62,232,255,0.06);
  color: var(--cyan);
  font-family: var(--font-m); font-size: 10px;
  letter-spacing: .15em; text-transform: uppercase;
  margin-bottom: 28px;
}
.bx-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--cyan);
  display: inline-block;
  animation: bx-ping 1.5s cubic-bezier(0,0,.2,1) infinite;
}
@keyframes bx-ping {
  75%, 100% { transform: scale(2.2); opacity: 0; }
}

/* ── Grid BG ── */
.bx-grid-bg {
  background-image:
    linear-gradient(rgba(62,232,255,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(62,232,255,0.025) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* ── Product cards ── */
.bx-product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 48px 0;
}
.bx-product-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 36px 30px;
  display: flex; flex-direction: column;
  transition: transform .25s, box-shadow .25s, border-color .25s;
  position: relative; overflow: hidden;
  text-decoration: none !important;
}
.bx-product-card::before {
  content: '';
  position: absolute; inset: 0; border-radius: inherit;
  opacity: 0; transition: opacity .3s;
}
.bx-product-card:hover { transform: translateY(-4px); }
.bx-product-card:hover::before { opacity: 1; }

.bx-card-cyan:hover    { border-color: rgba(62,232,255,0.35);   box-shadow: 0 20px 56px rgba(62,232,255,0.08); }
.bx-card-cyan::before  { background: linear-gradient(135deg, rgba(62,232,255,0.05) 0%, transparent 60%); }
.bx-card-indigo:hover  { border-color: rgba(129,140,248,0.35);  box-shadow: 0 20px 56px rgba(129,140,248,0.08); }
.bx-card-indigo::before{ background: linear-gradient(135deg, rgba(129,140,248,0.05) 0%, transparent 60%); }
.bx-card-amber:hover   { border-color: rgba(251,191,36,0.35);   box-shadow: 0 20px 56px rgba(251,191,36,0.06); }
.bx-card-amber::before { background: linear-gradient(135deg, rgba(251,191,36,0.05) 0%, transparent 60%); }

.bx-card-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; margin-bottom: 24px;
  border: 1px solid transparent;
}
.bx-icon-cyan   { background: rgba(62,232,255,0.08);  border-color: rgba(62,232,255,0.2); }
.bx-icon-indigo { background: rgba(129,140,248,0.08); border-color: rgba(129,140,248,0.2); }
.bx-icon-amber  { background: rgba(251,191,36,0.08);  border-color: rgba(251,191,36,0.2); }

.bx-card-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 100px;
  font-family: var(--font-m); font-size: 9px;
  letter-spacing: .1em; text-transform: uppercase;
  margin-bottom: 14px;
}
.bx-badge-cyan   { background: rgba(62,232,255,0.06);  border: 1px solid rgba(62,232,255,0.2);  color: var(--cyan); }
.bx-badge-indigo { background: rgba(129,140,248,0.06); border: 1px solid rgba(129,140,248,0.2); color: var(--indigo); }
.bx-badge-amber  { background: rgba(251,191,36,0.06);  border: 1px solid rgba(251,191,36,0.2);  color: var(--amber); }

.bx-card-title {
  font-family: var(--font-d); font-size: 20px; font-weight: 700;
  color: var(--text-1); margin-bottom: 10px; letter-spacing: -.01em;
}
.bx-card-desc {
  font-size: 13.5px; line-height: 1.75; color: var(--text-2);
  flex-grow: 1; margin-bottom: 28px;
}
.bx-card-link {
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--font-m); font-size: 11px; font-weight: 500;
  letter-spacing: .1em; text-transform: uppercase;
  text-decoration: none; transition: gap .2s;
}
.bx-card-link:hover { gap: 14px; }
.bx-link-cyan   { color: var(--cyan); }
.bx-link-indigo { color: var(--indigo); }
.bx-link-amber  { color: var(--amber); }

/* ── Stats strip ── */
.bx-stats {
  display: flex; justify-content: center; gap: 0;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: rgba(11,18,37,0.5);
  backdrop-filter: blur(12px);
  overflow: hidden;
  max-width: 560px;
  margin: 0 auto 64px;
}
.bx-stat {
  flex: 1; padding: 20px 24px; text-align: center;
  border-right: 1px solid var(--border);
}
.bx-stat:last-child { border-right: none; }
.bx-stat-val   { font-family: var(--font-d); font-size: 26px; font-weight: 800; color: var(--cyan); letter-spacing: -.02em; }
.bx-stat-label { font-family: var(--font-m); font-size: 9px; letter-spacing: .2em; text-transform: uppercase; color: var(--text-3); margin-top: 4px; }

/* ── How it works ── */
.bx-steps {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; margin: 0 0 80px;
}
.bx-step {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 18px; padding: 32px 26px;
}
.bx-step-n {
  font-family: var(--font-d); font-size: 11px; font-weight: 700;
  color: var(--cyan); text-transform: uppercase; letter-spacing: .15em;
  margin-bottom: 16px; display: flex; align-items: center; gap: 8px;
}
.bx-step-n::before { content:''; display:inline-block; width:20px; height:1px; background:var(--cyan); }
.bx-step h4 { font-family: var(--font-d); font-size: 17px; font-weight: 700; color: var(--text-1); margin-bottom: 8px; }
.bx-step p  { font-size: 13px; line-height: 1.7; color: var(--text-2); }

/* ── Section header ── */
.bx-section-hdr { text-align: center; margin-bottom: 52px; }
.bx-section-hdr h2 { font-family: var(--font-d); font-size: clamp(24px,3.5vw,38px); font-weight: 800; letter-spacing: -.02em; color: var(--text-1); margin: 12px 0 16px; }
.bx-section-hdr p  { font-size: 15px; color: var(--text-2); max-width: 480px; margin: 0 auto; line-height: 1.7; }
.bx-accent-line { width: 40px; height: 3px; background: linear-gradient(90deg, var(--cyan), #4f8fff); border-radius: 2px; margin: 0 auto; }

/* ── Footer ── */
.bx-footer {
  border-top: 1px solid var(--border);
  padding: 56px 0 28px;
  margin-top: 80px;
}
.bx-footer-inner {
  display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 48px;
}
.bx-footer-brand p { font-size: 12.5px; color: var(--text-3); line-height: 1.7; margin: 14px 0 20px; max-width: 280px; }
.bx-footer-col h5 { font-family: var(--font-d); font-size: 10px; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; color: var(--text-1); margin-bottom: 18px; }
.bx-footer-col ul { list-style: none; padding: 0; }
.bx-footer-col li { margin-bottom: 9px; }
.bx-footer-col a { font-size: 12.5px; color: var(--text-3); text-decoration: none; transition: color .2s; }
.bx-footer-col a:hover { color: var(--cyan); }
.bx-footer-bottom { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; padding-top: 24px; border-top: 1px solid var(--border); }
.bx-footer-bottom p, .bx-footer-bottom a { font-family: var(--font-m); font-size: 9px; letter-spacing: .15em; text-transform: uppercase; color: var(--text-3); text-decoration: none; }
.bx-footer-bottom a:hover { color: var(--text-2); }
.bx-social { display: flex; gap: 10px; }
.bx-social-link { width: 34px; height: 34px; border-radius: 8px; background: var(--surface); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; color: var(--text-3); font-size: 13px; text-decoration: none; transition: border-color .2s, color .2s, background .2s; }
.bx-social-link:hover { border-color: rgba(62,232,255,0.3); color: var(--cyan); background: rgba(62,232,255,0.06); }

/* Responsive */
@media (max-width: 768px) {
  .bx-product-grid { grid-template-columns: 1fr; }
  .bx-steps        { grid-template-columns: 1fr; }
  .bx-footer-inner { grid-template-columns: 1fr 1fr; }
  .bx-stats        { flex-direction: column; max-width: 100%; }
  .bx-stat         { border-right: none; border-bottom: 1px solid var(--border); }
  .bx-stat:last-child { border-bottom: none; }
  .bx-nav          { margin: 0; }
}
@media (max-width: 480px) {
  .bx-footer-inner { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── Nav ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bx-nav">
  <div class="bx-logo">
    <div class="bx-logo-icon">⬡</div>
    Bayantx<span>360</span>
  </div>
  <div style="display:flex;align-items:center;gap:28px;">
    <a href="#products" style="font-family:'Syne',sans-serif;font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#8a9bbf;text-decoration:none;">Products</a>
    <a href="#how"      style="font-family:'Syne',sans-serif;font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:#8a9bbf;text-decoration:none;">How It Works</a>
    <a href="mailto:hello@bayantx360.com" style="font-family:'Syne',sans-serif;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#03050d;background:#3ee8ff;padding:8px 18px;border-radius:8px;text-decoration:none;">Contact</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bx-hero bx-grid-bg">
  <div class="bx-tag">
    <span class="bx-dot"></span>
    3 Live Products · Early Access Open
  </div>
  <h1>
    Research & Analytics<br>
    <span class="bx-grad">Without the Code</span>
  </h1>
  <p>
    Bayantx360 gives researchers, economists, and data teams powerful
    AI-driven analytical tools through guided no-code interfaces.
    Publication-ready outputs. Zero programming required.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Stats strip ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="bx-stats">
  <div class="bx-stat">
    <div class="bx-stat-val">3</div>
    <div class="bx-stat-label">Live Products</div>
  </div>
  <div class="bx-stat">
    <div class="bx-stat-val">0</div>
    <div class="bx-stat-label">Lines of Code Required</div>
  </div>
  <div class="bx-stat">
    <div class="bx-stat-val">Free</div>
    <div class="bx-stat-label">To Get Started</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Products section ──────────────────────────────────────────────────────────
st.markdown('<div id="products"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="bx-section-hdr">
  <div class="bx-tag">Product Ecosystem</div>
  <h2>One Platform. Every Analytical Workflow.</h2>
  <div class="bx-accent-line" style="margin:16px auto 0;"></div>
  <p style="margin-top:16px;">Each tool is purpose-built for a specific research or analytics task.
  Pick the one you need — they're all free to try.</p>
</div>
""", unsafe_allow_html=True)

# Product cards rendered via Streamlit columns for the navigation buttons
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown("""
    <div class="bx-product-card bx-card-cyan">
      <div class="bx-card-icon bx-icon-cyan">📐</div>
      <div class="bx-card-badge bx-badge-cyan">⚡ Panel Regression</div>
      <div class="bx-card-title">PanelStatX</div>
      <div class="bx-card-desc">
        Run OLS, Fixed Effects, and Random Effects models on your panel dataset.
        Get publication-ready regression tables and diagnostic reports —
        automatically generated, zero code.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_PanelStatX.py", label="Open PanelStatX →", use_container_width=True)

with c2:
    st.markdown("""
    <div class="bx-product-card bx-card-indigo">
      <div class="bx-card-icon bx-icon-indigo">🧬</div>
      <div class="bx-card-badge bx-badge-indigo">🛡 Privacy-Safe Data</div>
      <div class="bx-card-title">DataSynthX</div>
      <div class="bx-card-desc">
        Generate synthetic datasets that statistically mirror your real data.
        Share, test, and train models without ever exposing sensitive records —
        distributions and correlations preserved.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_DataSynthX.py", label="Open DataSynthX →", use_container_width=True)

with c3:
    st.markdown("""
    <div class="bx-product-card bx-card-amber">
      <div class="bx-card-icon bx-icon-amber">🔬</div>
      <div class="bx-card-badge bx-badge-amber">✓ Construct Validity</div>
      <div class="bx-card-title">EFActor</div>
      <div class="bx-card-desc">
        Run Exploratory and Confirmatory Factor Analysis through a guided interface.
        Upload your survey data, get KMO, CFI, and RMSEA diagnostics instantly —
        without touching a line of code.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_EFActor.py", label="Open EFActor →", use_container_width=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<div id="how"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="bx-section-hdr" style="margin-top:72px;">
  <div class="bx-tag">How It Works</div>
  <h2>From Raw Data to Insight in Three Steps</h2>
  <div class="bx-accent-line" style="margin:16px auto 0;"></div>
  <p style="margin-top:16px;">
    Your data never leaves the platform. Everything runs in a private,
    isolated session — you stay in control from upload to export.
  </p>
</div>

<div class="bx-steps">
  <div class="bx-step">
    <div class="bx-step-n">Step 01</div>
    <h4>Upload Your Data</h4>
    <p>Drop in a CSV or Excel file. The platform auto-detects structure,
    validates your dataset, and flags any issues before you proceed.</p>
  </div>
  <div class="bx-step">
    <div class="bx-step-n">Step 02</div>
    <h4>Configure Your Analysis</h4>
    <p>Select your model and set parameters through guided visual controls.
    Real-time validation prevents errors before they happen.</p>
  </div>
  <div class="bx-step">
    <div class="bx-step-n">Step 03</div>
    <h4>Export Results</h4>
    <p>Receive formatted tables, diagnostic charts, and annotated reports
    ready for academic submission or stakeholder presentations.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Who it's for ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="bx-section-hdr">
  <div class="bx-tag">Built For</div>
  <h2>The Modern Knowledge Worker</h2>
  <div class="bx-accent-line" style="margin:16px auto 0;"></div>
</div>
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-bottom:80px;">
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">🎓 Academic Researchers</span>
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">📈 Econometricians</span>
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">🧪 PhD Students</span>
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">🏛 Policy Analysts</span>
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">💾 Data Scientists</span>
  <span style="display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:100px;background:#0f1a30;border:1px solid rgba(255,255,255,0.07);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;color:#8a9bbf;">🏢 Enterprise Teams</span>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bx-footer">
  <div class="bx-footer-inner">
    <div class="bx-footer-brand">
      <div class="bx-logo" style="margin-bottom:0;">
        <div class="bx-logo-icon">⬡</div>
        Bayantx<span style="color:#3ee8ff;">360</span>
      </div>
      <p>No-code AI tools for researchers, economists, and data teams.
         Publication-ready outputs without the programming overhead.</p>
      <div class="bx-social">
        <a href="https://x.com/bayantx360"                    class="bx-social-link" target="_blank">𝕏</a>
        <a href="https://www.linkedin.com/company/bayantx360/" class="bx-social-link" target="_blank">in</a>
        <a href="#"                                            class="bx-social-link">◈</a>
      </div>
    </div>

    <div class="bx-footer-col">
      <h5>Products</h5>
      <ul>
        <li><a href="pages/1_PanelStatX">PanelStatX</a></li>
        <li><a href="pages/2_DataSynthX">DataSynthX</a></li>
        <li><a href="pages/3_EFActor">EFActor</a></li>
      </ul>
    </div>

    <div class="bx-footer-col">
      <h5>Company</h5>
      <ul>
        <li><a href="#">About</a></li>
        <li><a href="#">Blog</a></li>
        <li><a href="#">Careers</a></li>
        <li><a href="#">Partners</a></li>
      </ul>
    </div>

    <div class="bx-footer-col">
      <h5>Get in Touch</h5>
      <ul>
        <li><a href="mailto:hello@bayantx360.com">hello@bayantx360.com</a></li>
        <li><a href="#">Support</a></li>
        <li><a href="#">Status</a></li>
        <li><a href="#">Terms of Service</a></li>
        <li><a href="#">Privacy Policy</a></li>
      </ul>
    </div>
  </div>

  <div class="bx-footer-bottom">
    <p>© 2026 Bayantx360. All rights reserved.</p>
    <div style="display:flex;gap:24px;">
      <a href="#">Terms of Service</a>
      <a href="#">Privacy Policy</a>
      <a href="#">Cookie Policy</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

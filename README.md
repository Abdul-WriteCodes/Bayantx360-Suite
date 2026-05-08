# ⬡ Bayantx360 Suite

**Three statistical tools. One access key. Zero friction.**

PanelStatX · DataSynthX · EFActor — unified under a single credit-based authentication system with shared Google Sheets backend, live credit balance, and a premium SaaS landing page.

---

## File Structure

```
bayantx360_suite/
├── suite_home.py              ← Entry point: landing page + auth gate + app selector
├── requirements.txt
├── README.md
│
├── shared/
│   ├── __init__.py
│   ├── auth.py                ← Unified auth + credit engine (single source of truth)
│   └── theme.py               ← Suite CSS + Plotly theme (imported by all apps)
│
├── pages/
│   ├── __init__.py
│   ├── panelstatx.py          ← Panel Econometrics app
│   ├── datasynthx.py          ← Synthetic Data app
│   └── efactor.py             ← Psychometric Analysis app
│
└── .streamlit/
    ├── config.toml            ← Streamlit server + theme config
    ├── pages.toml             ← Multi-page routing
    └── secrets.toml.template  ← Secrets schema (copy → secrets.toml, fill values)
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure secrets

Copy the template and fill in your values:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Required secrets:

| Key | Description |
|-----|-------------|
| `BAYANTX_SHEET_ID` | Google Sheet ID for the unified keys sheet |
| `OPENAI_API_KEY` | OpenAI API key (for AI explainer features) |
| `gcp_service_account` | GCP service account JSON (for Sheets API) |

### 3. Google Sheet schema

Create a Google Sheet with the following columns in **Sheet1**:

| A: Key | B: Credits | C: DatePurchased | D: Email |
|--------|------------|-----------------|---------|
| BTX-XXXX-XXXX-XXXX | 40 | 2025-01-15 | user@example.com |

Share the sheet with your service account email (Editor access).

### 4. Run locally

```bash
streamlit run suite_home.py
```

### 5. Deploy to Streamlit Cloud

- Set the main file to `suite_home.py`
- Add all secrets from `secrets.toml` in the Streamlit Cloud dashboard
- No other configuration needed

---

## Migration from Standalone Apps

The three standalone apps (`app__28_.py`, `app__27_.py`, `app__26_.py`) each had:
- Their own Google Sheet secret (`SHEET_ID`, `DSX_SHEET_ID`, `EFACTOR_SHEET_ID`)
- Their own auth/credit functions duplicated in each file
- Their own CSS blocks with slight visual inconsistencies
- No connection between apps — separate sessions, separate balances

The suite replaces all of that with:

| Concern | Before | After |
|---------|--------|-------|
| Google Sheet | 3 separate sheets | 1 unified sheet (`BAYANTX_SHEET_ID`) |
| Auth functions | Duplicated in each file | `shared/auth.py` — imported once |
| CSS | 3 near-identical blocks | `shared/theme.py` — applied uniformly |
| Credit deduction | Key-string lookup each time | Row-index cached on login (faster) |
| Trial gate | Inconsistent across apps | Standardised `is_free_trial` flag |
| Navigation | No connection | App selector + `st.switch_page()` |

---

## Adding a New App

The architecture is designed for zero-friction expansion:

1. Create `pages/newapp.py`
2. Add two import lines at the top:
   ```python
   from shared.auth import init_session_state, refresh_credits, render_credit_hud, ...
   from shared.theme import apply_suite_css, apply_theme
   ```
3. Add one entry to the `APPS` list in `suite_home.py`
4. Register the page in `.streamlit/pages.toml`

No changes needed to `shared/auth.py`, the Google Sheet, or any existing app.

---

## Credit System

| Event | Credit cost |
|-------|-------------|
| PanelStatX — AI explainer | 1 credit |
| PanelStatX — DOCX report | 1 credit |
| DataSynthX — AI analysis | 1 credit |
| DataSynthX — CSV/Excel export | 0–5 credits (row-based) |
| EFActor — Data export | 1–5 credits (row-based) |
| EFActor — DOCX report | 1 credit |
| EFActor — ZIP bundle | Combined cost |
| All analysis (models, EFA, synthesis) | **Free — always** |

### Free Trial

| Feature | Trial | Paid |
|---------|-------|------|
| All analysis | ✅ Unlimited | ✅ Unlimited |
| On-screen results | ✅ Full | ✅ Full |
| AI explainer | 🔒 Locked | ✅ 1 credit |
| All exports (DOCX, CSV, Excel, ZIP) | 🔒 Locked | ✅ Credit cost |

---

## Pricing (Suite)

| Plan | Price | Credits |
|------|-------|---------|
| Starter | $10 | 10 credits |
| Standard | $30 | 40 credits |
| Team | $100 | 150 credits |

Credits are shared across all apps. Never expire.

---

## Security Notes

- Single access key unlocks the entire suite — treat it like a password
- Key validation reads from Google Sheets on every login (not cached)
- Credit balance is refreshed from the sheet on every authenticated page load
- Trial sessions have no sheet row — no write operations for trial users
- `st.secrets` is used for all sensitive values — never hardcoded

---

## Support

- Twitter/X: [@bayantx360](https://x.com/bayantx360)
- Email: bayantx360@gmail.com
- User Guide: [Box link](https://app.box.com/s/vw4c6u10bv0z8ngarzj73ej18t74e3wl)

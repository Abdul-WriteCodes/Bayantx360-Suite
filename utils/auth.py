"""
utils/auth.py
─────────────────────────────────────────────────────────────────────────────
Shared authentication and credit engine for the Bayantx360 ecosystem.

All three products (PanelStatX, DataSynthX, EFActor) use a single Google
Sheet as the credential store.  Each product has its own sheet key in
st.secrets, but the logic here is identical — only the secret key name
and the session-state namespace differ.

Expected secrets layout (in .streamlit/secrets.toml):
─────────────────────────────────────────────────────
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
...

PANELSTATX_SHEET_ID  = "..."   # PanelStatX credits sheet
DSX_SHEET_ID         = "..."   # DataSynthX credits sheet
EFACTOR_SHEET_ID     = "..."   # EFActor credits sheet
─────────────────────────────────────────────────────

Sheet columns (in this exact order):
    Key | Credits | DatePurchased | Email

Session state keys written by this module (namespaced by product):
    bx360_authenticated    bool
    bx360_is_free_trial    bool
    bx360_access_key       str
    bx360_key_owner        str   (email)
    bx360_credits          int
    bx360_row_index        int   (1-based sheet row)
    bx360_product          str   ("panelstatx" | "datasynthx" | "efactor")
"""

from __future__ import annotations

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ── Sheet schema ──────────────────────────────────────────────────────────────
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
_SHEET_TAB      = "Sheet1"
_COL_KEY        = "Key"
_COL_CREDITS    = "Credits"
_COL_ISSUED     = "DatePurchased"
_COL_OWNER      = "Email"
_REQUIRED_HDRS  = [_COL_KEY, _COL_CREDITS, _COL_ISSUED, _COL_OWNER]

# Map product slug → secrets key for the spreadsheet ID
_PRODUCT_SHEET_SECRET: dict[str, str] = {
    "panelstatx": "PANELSTATX_SHEET_ID",
    "datasynthx": "DSX_SHEET_ID",
    "efactor":    "EFACTOR_SHEET_ID",
}


# ── Internal helpers ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _gsheet_client() -> gspread.Client:
    """Cached GSheets client (shared across all products)."""
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=_SCOPES
    )
    return gspread.authorize(creds)


def _worksheet(product: str) -> gspread.Worksheet:
    secret_key = _PRODUCT_SHEET_SECRET[product]
    sheet_id   = st.secrets[secret_key]
    return _gsheet_client().open_by_key(sheet_id).worksheet(_SHEET_TAB)


def _all_records(product: str) -> list[dict]:
    ws      = _worksheet(product)
    records = ws.get_all_records(
        expected_headers=_REQUIRED_HDRS,
        value_render_option="UNFORMATTED_VALUE",
    )
    return [r for r in records if any(str(v).strip() for v in r.values())]


# ── Public API ────────────────────────────────────────────────────────────────

def validate_key(product: str, access_key: str) -> dict | None:
    """
    Return the sheet row dict if the key exists and has credits, else None.
    Raises a Streamlit error on sheet access failure.
    """
    try:
        for row in _all_records(product):
            if str(row.get(_COL_KEY, "")).strip() == access_key.strip():
                return row
        return None
    except Exception as exc:
        st.error(f"Key validation error: {exc}")
        return None


def get_credits(product: str, access_key: str) -> int:
    """Fetch live credit balance for the given key."""
    try:
        for row in _all_records(product):
            if str(row.get(_COL_KEY, "")).strip() == access_key.strip():
                return int(row.get(_COL_CREDITS, 0))
        return 0
    except Exception:
        return 0


def deduct_credits(product: str, access_key: str, amount: int = 1) -> int:
    """
    Deduct `amount` credits from the sheet row for this key.
    Returns the new balance.
    """
    try:
        ws      = _worksheet(product)
        records = _all_records(product)
        header  = ws.row_values(1)
        col_idx = header.index(_COL_CREDITS) + 1   # 1-based
        for i, row in enumerate(records):
            if str(row.get(_COL_KEY, "")).strip() == access_key.strip():
                row_num  = i + 2                    # +1 header, +1 0-based
                current  = int(row.get(_COL_CREDITS, 0))
                new_val  = max(0, current - amount)
                ws.update_cell(row_num, col_idx, new_val)
                return new_val
        return 0
    except Exception as exc:
        st.error(f"Credit deduction error: {exc}")
        return 0


def credit_cost(n_rows: int) -> int:
    """
    Tiered export credit cost used consistently across all products.
        ≤ 300 rows  → 1 credit
        ≤ 1 000 rows → 2 credits
        > 1 000 rows → 5 credits
    """
    if n_rows <= 300:
        return 1
    elif n_rows <= 1_000:
        return 2
    return 5


# ── Session-state helpers ─────────────────────────────────────────────────────

def is_authenticated() -> bool:
    return bool(st.session_state.get("bx360_authenticated", False))


def is_free_trial() -> bool:
    return bool(st.session_state.get("bx360_is_free_trial", False))


def current_credits() -> int:
    return int(st.session_state.get("bx360_credits", 0))


def current_product() -> str:
    return st.session_state.get("bx360_product", "")


def login_free_trial(product: str) -> None:
    st.session_state.update({
        "bx360_authenticated": True,
        "bx360_is_free_trial": True,
        "bx360_access_key":    "FREE-TRIAL",
        "bx360_key_owner":     "Free Trial",
        "bx360_credits":       0,
        "bx360_row_index":     None,
        "bx360_product":       product,
    })


def login_with_key(product: str, row: dict) -> None:
    st.session_state.update({
        "bx360_authenticated": True,
        "bx360_is_free_trial": False,
        "bx360_access_key":    str(row.get(_COL_KEY, "")).strip(),
        "bx360_key_owner":     str(row.get(_COL_OWNER, "User")),
        "bx360_credits":       int(row.get(_COL_CREDITS, 0)),
        "bx360_row_index":     None,   # not needed; we look up by key
        "bx360_product":       product,
    })


def logout(extra_keys: list[str] | None = None) -> None:
    """Clear all bx360_ session state keys plus any product-specific extras."""
    bx360_keys = [k for k in st.session_state if k.startswith("bx360_")]
    for k in bx360_keys + (extra_keys or []):
        st.session_state.pop(k, None)


def refresh_credits(product: str) -> int:
    """Re-fetch live balance from sheet and update session state."""
    key     = st.session_state.get("bx360_access_key", "")
    balance = get_credits(product, key)
    st.session_state["bx360_credits"] = balance
    return balance


def spend_credits(product: str, amount: int = 1) -> int:
    """Deduct credits and update session state. Returns new balance."""
    key     = st.session_state.get("bx360_access_key", "")
    new_bal = deduct_credits(product, key, amount)
    st.session_state["bx360_credits"] = new_bal
    return new_bal

"""Shared helpers: formatting, badges, CSS injection."""
from __future__ import annotations
import streamlit as st


# ---------- Formatting ----------
def money(value: float, decimals: int = 0) -> str:
    """$1.24M / $842K / $12,400"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1_000_000:
        return f"{sign}${v/1_000_000:.2f}M" if decimals else f"{sign}${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{sign}${v/1_000:.0f}K"
    return f"{sign}${v:,.0f}"


def pct(value: float, decimals: int = 1) -> str:
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return "—"


def risk_badge(level: str) -> str:
    level = (level or "").lower()
    mapping = {
        "critical": ("#B91C1C", "#FEE2E2", "CRITICAL"),
        "high":     ("#B45309", "#FEF3C7", "HIGH"),
        "medium":   ("#A16207", "#FEF9C3", "MEDIUM"),
        "watch":    ("#A16207", "#FEF9C3", "WATCH"),
        "low":      ("#15803D", "#DCFCE7", "LOW"),
        "healthy":  ("#15803D", "#DCFCE7", "HEALTHY"),
        "at risk":  ("#B91C1C", "#FEE2E2", "AT RISK"),
    }
    color, bg, label = mapping.get(level, ("#334155", "#E2E8F0", level.upper() or "—"))
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
        f'background:{bg};color:{color};font-size:11px;font-weight:600;'
        f'letter-spacing:0.4px;">{label}</span>'
    )


def status_badge(status: str) -> str:
    s = (status or "").lower()
    palette = {
        "awarded":     ("#15803D", "#DCFCE7"),
        "approved":    ("#15803D", "#DCFCE7"),
        "paid":        ("#15803D", "#DCFCE7"),
        "healthy":     ("#15803D", "#DCFCE7"),
        "submitted":   ("#1D4ED8", "#DBEAFE"),
        "estimating":  ("#1D4ED8", "#DBEAFE"),
        "research":    ("#475569", "#E2E8F0"),
        "negotiation": ("#7C3AED", "#EDE9FE"),
        "pending":     ("#B45309", "#FEF3C7"),
        "under review":("#B45309", "#FEF3C7"),
        "watch":       ("#B45309", "#FEF3C7"),
        "rejected":    ("#B91C1C", "#FEE2E2"),
        "lost":        ("#B91C1C", "#FEE2E2"),
        "at risk":     ("#B91C1C", "#FEE2E2"),
        "critical":    ("#B91C1C", "#FEE2E2"),
    }
    color, bg = palette.get(s, ("#334155", "#E2E8F0"))
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
        f'background:{bg};color:{color};font-size:11px;font-weight:600;">'
        f'{(status or "").upper()}</span>'
    )


# ---------- CSS ----------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ===================================================================
           GLOBAL RESET & LAYOUT
           =================================================================== */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #0F172A !important;
        }
        .stApp { background: #F7F9FC; }
        .block-container {
            padding: 1rem 2.2rem 3rem 2.2rem;
            max-width: 1500px;
        }

        /* Push content down so it clears the top bar area */
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 1rem;
        }

        /* Tighten Streamlit's default top gap */
        [data-testid="stAppViewContainer"] .block-container > div:first-child {
            padding-top: 0 !important;
        }

        /* Reduce vertical gap between stacked widgets */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
            gap: 0.6rem;
        }

        /* Multiselect pills — make them compact */
        span[data-baseweb="tag"] {
            background-color: #1D4ED8 !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            font-size: 12px !important;
            height: 24px !important;
        }
        span[data-baseweb="tag"] span {
            color: #FFFFFF !important;
        }

        /* Make the header area of the app not overlap */
        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 2rem !important;
        }

        /* ===================================================================
           HEADINGS — FORCE VISIBILITY EVERYWHERE
           =================================================================== */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stHeadingWithActionElements"] h1,
        [data-testid="stHeadingWithActionElements"] h2,
        [data-testid="stHeadingWithActionElements"] h3,
        .main h1, .main h2, .main h3, .main h4,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4 {
            color: #0F172A !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            visibility: visible !important;
            opacity: 1 !important;
            display: block !important;
        }

        h1, .stMarkdown h1 { font-size: 26px !important; line-height: 1.3 !important; margin: 0.4rem 0 0.6rem 0 !important; }
        h2, .stMarkdown h2 { font-size: 20px !important; line-height: 1.35 !important; margin: 1rem 0 0.5rem 0 !important; }
        h3, .stMarkdown h3 { font-size: 16px !important; line-height: 1.4 !important; margin: 0.8rem 0 0.4rem 0 !important; }
        h4, .stMarkdown h4 { font-size: 14px !important; line-height: 1.4 !important; }

        /* Paragraphs & spans in the main content area */
        .stMarkdown p, .stMarkdown span, .stMarkdown div,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span {
            color: #0F172A;
        }

        /* Custom inline-styled page titles */
        [data-testid="stAppViewContainer"] div[style*="font-size:22px"],
        [data-testid="stAppViewContainer"] div[style*="font-size:24px"],
        [data-testid="stAppViewContainer"] div[style*="font-size:26px"] {
            color: #0F172A !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        /* ===================================================================
           SIDEBAR
           =================================================================== */
        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem;
        }

        /* Only style the radio group, NOT the outer label */
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: #0F172A !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            transition: background 0.15s ease;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #F1F5F9;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
            background: #EFF6FF;
        }

        /* Hide the built-in radio label entirely */
        section[data-testid="stSidebar"] .stRadio > label {
            display: none !important;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 2px;
        }

        /* Sidebar section headings */
        section[data-testid="stSidebar"] .ww-section,
        section[data-testid="stSidebar"] .ww-kpi-label {
            color: #64748B !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            letter-spacing: 0.8px !important;
            text-transform: uppercase !important;
            margin: 18px 0 8px 0 !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        /* Sidebar scroll safety */
        section[data-testid="stSidebar"] > div {
            overflow-y: auto !important;
        }

        /* ===================================================================
           CARDS
           =================================================================== */
        .ww-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        }

        .ww-kpi {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 16px 18px 14px 18px;
            box-shadow: 0 1px 2px rgba(15,23,42,0.04);
            height: 100%;
        }
        .ww-kpi-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.7px;
            color: #64748B;
            text-transform: uppercase;
        }
        .ww-kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #0F172A;
            margin: 6px 0 2px 0;
            letter-spacing: -0.02em;
        }
        .ww-kpi-trend {
            font-size: 12px;
            font-weight: 600;
            color: #15803D;
        }
        .ww-kpi-trend.neg { color: #B91C1C; }
        .ww-kpi-trend.warn { color: #B45309; }
        .ww-kpi-sub { font-size: 11.5px; color: #64748B; margin-top: 2px; }

        /* ===================================================================
           ALERTS
           =================================================================== */
        .ww-alert {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #1D4ED8;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }
        .ww-alert.warn  { border-left-color: #D97706; }
        .ww-alert.risk  { border-left-color: #DC2626; }
        .ww-alert.ok    { border-left-color: #16A34A; }
        .ww-alert-text { font-size: 13.5px; color: #1E293B; line-height: 1.45; }
        .ww-alert-tag {
            font-size: 10.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
            color: #64748B;
            text-transform: uppercase;
        }

        /* ===================================================================
           RISK CARDS
           =================================================================== */
        .ww-risk {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }
        .ww-risk.crit { border-left: 5px solid #DC2626; }
        .ww-risk.high { border-left: 5px solid #D97706; }
        .ww-risk.med  { border-left: 5px solid #CA8A04; }
        .ww-risk.low  { border-left: 5px solid #16A34A; }

        /* ===================================================================
           AI RESPONSE
           =================================================================== */
        .ww-ai {
            background: linear-gradient(180deg,#F8FAFF 0%,#FFFFFF 60%);
            border: 1px solid #DBEAFE;
            border-radius: 14px;
            padding: 18px 22px;
            margin-top: 12px;
        }
        .ww-ai-title {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: #1D4ED8;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .ww-ai-body { font-size: 14px; color: #1E293B; line-height: 1.6; }

        /* ===================================================================
           PILLS / BADGES
           =================================================================== */
        .ww-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* ===================================================================
           BUTTONS
           =================================================================== */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            font-size: 13.5px;
            padding: 8px 16px;
            border: 1px solid #CBD5E1;
            background: #FFFFFF;
            color: #0F172A;
            transition: all 0.15s ease;
        }
        .stButton > button:hover {
            border-color: #1D4ED8;
            color: #1D4ED8;
            background: #F8FAFF;
        }
        .stButton > button[kind="primary"] {
            background: #1D4ED8;
            color: #FFFFFF;
            border-color: #1D4ED8;
        }
        .stButton > button[kind="primary"]:hover {
            background: #1E40AF;
            border-color: #1E40AF;
            color: #FFFFFF;
        }

        /* ===================================================================
           TABLES
           =================================================================== */
        .ww-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .ww-table th {
            text-align: left;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.6px;
            color: #64748B;
            text-transform: uppercase;
            padding: 10px 12px;
            border-bottom: 1px solid #E2E8F0;
            background: #F8FAFC;
        }
        .ww-table td {
            padding: 11px 12px;
            border-bottom: 1px solid #F1F5F9;
            color: #1E293B;
        }
        .ww-table tr:hover td { background: #F8FAFF; }

        /* ===================================================================
           SECTION HEADERS
           =================================================================== */
        .ww-section {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: #64748B;
            text-transform: uppercase;
            margin: 22px 0 10px 0;
            display: block;
            visibility: visible;
            opacity: 1;
            line-height: 1.4;
        }

        /* ===================================================================
           DEMO PILL
           =================================================================== */
        .ww-demo {
            display: inline-block;
            background: #FEF3C7;
            color: #92400E;
            font-size: 10.5px;
            font-weight: 700;
            letter-spacing: 0.6px;
            padding: 3px 10px;
            border-radius: 999px;
            margin-left: 8px;
        }

        /* ===================================================================
           FINAL SAFETY OVERRIDE — ensures nothing disappears
           =================================================================== */
        [data-testid="stAppViewContainer"] *,
        .main * {
            visibility: visible;
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stAppViewContainer"] .stMarkdown strong,
        [data-testid="stAppViewContainer"] .stMarkdown b {
            color: #0F172A !important;
        }
        /* Extra safety: keep the main title clear of the Streamlit toolbar */
        .main .block-container {
            padding-top: 2.5rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
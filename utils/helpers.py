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
        /* ---------- Layout ---------- */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #0F172A;
        }
        .stApp { background: #F7F9FC; }
        .block-container {
            padding: 1.4rem 2.2rem 3rem 2.2rem;
            max-width: 1500px;
        }

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        section[data-testid="stSidebar"] * { color: #0F172A; }
        section[data-testid="stSidebar"] .stRadio > label {
            font-weight: 600;
            color: #64748B !important;
            font-size: 11px !important;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.15s ease;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
            background: #F1F5F9;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
            background: #EFF6FF;
        }

        /* ---------- Headings ---------- */
        h1, h2, h3, h4 { color: #0F172A; font-weight: 700; letter-spacing: -0.02em; }
        h1 { font-size: 26px !important; }
        h2 { font-size: 20px !important; margin-top: 1.2rem; }
        h3 { font-size: 16px !important; }

        /* ---------- Cards ---------- */
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

        /* ---------- Alerts ---------- */
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

        /* ---------- Risk cards ---------- */
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

        /* ---------- AI Response ---------- */
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

        /* ---------- Badges ---------- */
        .ww-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        /* ---------- Buttons ---------- */
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

        /* ---------- Tables ---------- */
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

        /* ---------- Section headers ---------- */
        .ww-section {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: #64748B;
            text-transform: uppercase;
            margin: 22px 0 10px 0;
        }

        /* ---------- Demo pill ---------- */
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
        </style>
        """,
        unsafe_allow_html=True,
    )
"""WaterWorks AI — Construction Intelligence for Water & Wastewater Infrastructure.

Run with: streamlit run app.py
"""
from __future__ import annotations
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import data as D
from utils import analytics as A
from utils import ai as AI
from utils import pdf as PDF
from utils.helpers import (
    inject_css, money, pct, risk_badge, status_badge
)

# ===========================================================================
# PAGE CONFIG
# ===========================================================================
st.set_page_config(
    page_title="WaterWorks AI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ===========================================================================
# SESSION STATE
# ===========================================================================
defaults = {
    "page": "Executive Dashboard",
    "selected_project": "WW-24018",
    "selected_bid": "BID-3001",
    "ai_estimate_result": None,
    "ai_quote_result": None,
    "ai_co_result": None,
    "quote_selected": None,
    "co_approved": set(),
    "search_query": "",
    "uploaded_df": None,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


# ===========================================================================
# LOAD DATA
# ===========================================================================
projects = D.load_projects()
bids = D.load_bids()
costs = D.load_costs()
vendors = D.load_vendors()
quotes = D.load_quotes()
cos = D.load_change_orders()
txns = D.load_transactions()

kpis = A.executive_kpis(projects, bids, cos, txns)
fin = A.financial_summary(projects, txns)
risks = A.scan_risks(projects, cos, txns)
risk_score, risk_label = A.portfolio_risk_score(risks)


# ===========================================================================
# SIDEBAR
# ===========================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding:6px 4px 18px 4px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.4px;color:#1D4ED8;">
            WATERWORKS AI
          </div>
          <div style="font-size:11.5px;color:#64748B;margin-top:4px;line-height:1.45;">
            Construction intelligence for complex infrastructure projects.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ww-section" style="margin-top:0;">NAVIGATION</div>',
                unsafe_allow_html=True)
    pages = [
        "Executive Dashboard",
        "Bid Opportunities",
        "Estimating",
        "Quote Comparison",
        "Projects",
        "Change Orders",
        "Financials",
        "Risk Center",
        "AI Assistant",
        "Settings",
    ]
    icons = {
        "Executive Dashboard": "▣",
        "Bid Opportunities": "◈",
        "Estimating": "▤",
        "Quote Comparison": "◫",
        "Projects": "▣",
        "Change Orders": "↗",
        "Financials": "$",
        "Risk Center": "⚠",
        "AI Assistant": "✦",
        "Settings": "⚙",
    }
    choice = st.radio(
        "Navigation",
        options=pages,
        format_func=lambda p: f"{icons.get(p,'•')}  {p}",
        index=pages.index(st.session_state["page"]),
        label_visibility="collapsed",
    )
    st.session_state["page"] = choice

    st.markdown(
        """
        <div style="position:relative;margin-top:24px;padding:12px 14px;
                    background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;">
          <div style="font-size:11px;font-weight:700;color:#0F172A;letter-spacing:0.4px;">
            DEMO WORKSPACE
          </div>
          <div style="font-size:11px;color:#64748B;margin-top:4px;">
            Last synced: Just now
          </div>
          <div style="font-size:11px;color:#64748B;margin-top:2px;">
            AI provider: <b>""" + AI.provider().upper() + """</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# TOP BAR (search + demo pill)
# ===========================================================================
top_l, top_m, top_r = st.columns([3, 1.4, 2.4])
with top_l:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;padding-top:4px;">'
        '<span style="font-size:20px;font-weight:700;color:#0F172A;">WaterWorks AI</span>'
        '<span class="ww-demo">DEMO MODE</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with top_r:
    st.session_state["search_query"] = st.text_input(
        "Search projects, bids, vendors, change orders",
        value=st.session_state["search_query"],
        placeholder="🔎  Search projects, bids, vendors, change orders…",
        label_visibility="collapsed",
    )


# ===========================================================================
# GLOBAL SEARCH RESULTS
# ===========================================================================
def render_search_results(q: str):
    if not q or len(q) < 2:
        return
    ql = q.lower()
    st.markdown('<div class="ww-section">GLOBAL SEARCH</div>', unsafe_allow_html=True)

    p = projects[projects.apply(
        lambda r: ql in str(r["project_id"]).lower() or ql in str(r["project_name"]).lower(),
        axis=1)]
    b = bids[bids.apply(
        lambda r: ql in str(r["opportunity_id"]).lower() or ql in str(r["project"]).lower(),
        axis=1)]
    v = vendors[vendors.apply(
        lambda r: ql in str(r["vendor_name"]).lower() or ql in str(r["trade"]).lower(),
        axis=1)]
    c = cos[cos.apply(
        lambda r: ql in str(r["co_id"]).lower() or ql in str(r["description"]).lower(),
        axis=1)]

    total = len(p) + len(b) + len(v) + len(c)
    if total == 0:
        st.info(f"No matches for “{q}”.")
        return

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"**Projects** · {len(p)}")
        for _, r in p.head(4).iterrows():
            st.markdown(f"- `{r['project_id']}` {r['project_name']}")
    with cols[1]:
        st.markdown(f"**Bids** · {len(b)}")
        for _, r in b.head(4).iterrows():
            st.markdown(f"- `{r['opportunity_id']}` {r['project']}")
    with cols[2]:
        st.markdown(f"**Vendors** · {len(v)}")
        for _, r in v.head(4).iterrows():
            st.markdown(f"- `{r['vendor_id']}` {r['vendor_name']}")
    with cols[3]:
        st.markdown(f"**Change Orders** · {len(c)}")
        for _, r in c.head(4).iterrows():
            st.markdown(f"- `{r['co_id']}` {r['description']}")
    st.markdown("---")


render_search_results(st.session_state["search_query"])


# ===========================================================================
# REUSABLE UI COMPONENTS
# ===========================================================================
def kpi_card(label: str, value: str, trend: str = "", sub: str = "", trend_class: str = ""):
    trend_html = ""
    if trend:
        trend_html = f'<div class="ww-kpi-trend {trend_class}">{trend}</div>'
    sub_html = f'<div class="ww-kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="ww-kpi">
          <div class="ww-kpi-label">{label}</div>
          <div class="ww-kpi-value">{value}</div>
          {trend_html}
          {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(text: str, kind: str = "info", tag: str = "ALERT"):
    cls = {"info": "", "warn": "warn", "risk": "risk", "ok": "ok"}.get(kind, "")
    st.markdown(
        f"""
        <div class="ww-alert {cls}">
          <div class="ww-alert-text">{text}</div>
          <div class="ww-alert-tag">{tag}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str):
    st.markdown(f'<div class="ww-section">{title}</div>', unsafe_allow_html=True)


def plotly_defaults(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="-apple-system, Segoe UI, Roboto, Arial", size=12, color="#0F172A"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor="#E2E8F0"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#E2E8F0"),
    )
    return fig


# ===========================================================================
# PAGE: EXECUTIVE DASHBOARD
# ===========================================================================
def page_dashboard():
    st.markdown(
        """
        <div style="margin-bottom:6px;">
          <div style="font-size:24px;font-weight:700;color:#0F172A;letter-spacing:-0.02em;">
            Good morning, Frontline Operations
          </div>
          <div style="font-size:14px;color:#64748B;margin-top:4px;">
            Here's what needs your attention across active projects and bids.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section("PORTFOLIO SNAPSHOT")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi_card("ACTIVE PROJECTS", str(kpis["active_projects"]),
                      "↑ 2 vs last month", "8 in execution")
    with c2: kpi_card("BACKLOG", money(kpis["backlog"]),
                      "↑ 4.1% vs forecast", "Contracted revenue")
    with c3: kpi_card("PIPELINE", money(kpis["pipeline"]),
                      "↑ 6.2% vs forecast", "Weighted probability")
    with c4: kpi_card("PROJECTED PROFIT", money(kpis["projected_profit"]),
                      "↑ 8.4% vs forecast", "Across active portfolio")
    with c5: kpi_card("AT-RISK VALUE", money(kpis["at_risk_value"]),
                      "↓ 0.9% vs forecast", "3 projects flagged", trend_class="warn")
    with c6: kpi_card("OUTSTANDING PAYMENTS", money(kpis["outstanding"]),
                      "↑ $120K vs last week", "Receivables aging", trend_class="warn")

    # ---- charts row 1 ----
    section("PROJECT PROFITABILITY")
    prof = A.profitability_frame(projects).sort_values("contract_value", ascending=False).head(8)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=prof["project_id"], y=prof["budget"],
                         name="Budget", marker_color="#CBD5E1"))
    fig.add_trace(go.Bar(x=prof["project_id"], y=prof["actual_cost"],
                         name="Actual Cost", marker_color="#60A5FA"))
    fig.add_trace(go.Bar(x=prof["project_id"], y=prof["forecast_cost"],
                         name="Forecast Cost", marker_color="#1D4ED8"))
    fig.add_trace(go.Bar(x=prof["project_id"], y=prof["Projected Profit"],
                         name="Projected Profit", marker_color="#16A34A"))
    fig.update_layout(barmode="group", yaxis_title="USD")
    plotly_defaults(fig, height=360)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    row_l, row_r = st.columns([1.4, 1])
    with row_l:
        section("REVENUE VS COST")
        rc = A.monthly_revenue_cost(projects)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=rc["month"], y=rc["revenue"], name="Revenue",
                                  mode="lines", fill="tozeroy",
                                  line=dict(color="#1D4ED8", width=2),
                                  fillcolor="rgba(29,78,216,0.10)"))
        fig2.add_trace(go.Scatter(x=rc["month"], y=rc["cost"], name="Cost",
                                  mode="lines", fill="tozeroy",
                                  line=dict(color="#94A3B8", width=2),
                                  fillcolor="rgba(148,163,184,0.15)"))
        plotly_defaults(fig2, height=320)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with row_r:
        section("PROJECT RISK DISTRIBUTION")
        counts = projects["risk_level"].value_counts().reindex(
            ["Healthy", "Watch", "At Risk", "Critical"]).fillna(0)
        fig3 = px.pie(
            names=counts.index, values=counts.values,
            color=counts.index,
            color_discrete_map={
                "Healthy": "#16A34A", "Watch": "#D97706",
                "At Risk": "#EA580C", "Critical": "#DC2626",
            },
            hole=0.62,
        )
        fig3.update_traces(textinfo="label+value", textfont_size=12)
        plotly_defaults(fig3, height=320)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    # ---- bid pipeline ----
    section("BID PIPELINE")
    stages = ["Research", "Estimating", "Internal Review", "Submitted", "Negotiation", "Awarded", "Lost"]
    counts = bids["status"].value_counts().reindex(stages).fillna(0).astype(int)
    values = bids.groupby("status")["estimated_value"].sum().reindex(stages).fillna(0)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=counts.index, y=counts.values,
        marker_color="#1D4ED8", name="Count",
        text=counts.values, textposition="outside",
        customdata=values.values,
        hovertemplate="<b>%{x}</b><br>Bids: %{y}<br>Value: $%{customdata:,.0f}<extra></extra>",
    ))
    plotly_defaults(fig4, height=300)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # ---- alerts ----
    section("MANAGEMENT ALERTS")
    alerts = [
        ("warn", "WW-24018 is trending 7.3% below expected margin."),
        ("warn", "Change order CO-1048 has been pending for 12 days."),
        ("warn", "Vendor quote Q-5003 expires in 3 days."),
        ("risk", "Project WW-24011 has $420K outstanding."),
        ("ok",   "Project WW-24015 is 6% ahead of schedule."),
    ]
    for kind, text in alerts:
        alert_card(text, kind=kind)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    d1, d2 = st.columns([1, 1])
    with d1:
        if st.button("Generate Executive Report", type="primary", use_container_width=True):
            pdf_bytes = PDF.build_report(kpis, fin, projects, risks, cos, risk_score, risk_label)
            st.download_button(
                "⬇  Download PDF",
                data=pdf_bytes,
                file_name=f"WaterWorks-AI-Executive-Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    with d2:
        if st.button("Open AI Decision Center", use_container_width=True):
            st.session_state["page"] = "AI Assistant"
            st.rerun()


# ===========================================================================
# PAGE: BID OPPORTUNITIES
# ===========================================================================
def page_bids():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">Bid Opportunities</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Active pursuit pipeline across Oregon and Washington water & wastewater infrastructure.
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        status_filter = st.multiselect(
            "Status", options=sorted(bids["status"].unique()),
            default=sorted(bids["status"].unique()))
    with f2:
        type_filter = st.multiselect(
            "Project Type", options=sorted(bids["project_type"].unique()),
            default=sorted(bids["project_type"].unique()))
    with f3:
        est_filter = st.multiselect(
            "Estimator", options=sorted(bids["estimator"].unique()),
            default=sorted(bids["estimator"].unique()))

    view = st.radio("View", ["Table", "Kanban"], horizontal=True, label_visibility="collapsed")

    df = bids[bids["status"].isin(status_filter) &
              bids["project_type"].isin(type_filter) &
              bids["estimator"].isin(est_filter)].copy()

    if view == "Table":
        show = df.copy()
        show["Estimated Value"] = show["estimated_value"].apply(money)
        show["Bid Due"] = show["bid_due"].dt.strftime("%b %d, %Y")
        show["Probability"] = show["probability"].apply(lambda x: f"{x}%")
        show = show[["opportunity_id", "project", "owner", "location",
                     "project_type", "Estimated Value", "Bid Due",
                     "Probability", "estimator", "status"]]
        show.columns = ["ID", "Project", "Owner", "Location", "Type",
                        "Est. Value", "Bid Due", "Win %", "Estimator", "Status"]
        st.dataframe(show, use_container_width=True, hide_index=True, height=520)
    else:
        cols = st.columns(5)
        columns = {
            "Research": cols[0], "Estimating": cols[1],
            "Internal Review": cols[2], "Submitted": cols[3],
            "Negotiation": cols[4],
        }
        for stage, col in columns.items():
            with col:
                st.markdown(
                    f'<div style="font-size:11px;font-weight:700;color:#64748B;'
                    f'letter-spacing:0.6px;margin-bottom:8px;">{stage.upper()}</div>',
                    unsafe_allow_html=True,
                )
                sub = df[df["status"] == stage]
                for _, b in sub.iterrows():
                    st.markdown(
                        f"""
                        <div class="ww-card" style="padding:12px 14px;margin-bottom:8px;">
                          <div style="font-size:11px;color:#64748B;font-weight:600;">
                            {b['opportunity_id']}</div>
                          <div style="font-size:13px;font-weight:600;color:#0F172A;
                                      margin:4px 0;">{b['project']}</div>
                          <div style="font-size:11.5px;color:#64748B;">
                            {money(b['estimated_value'])} · {b['probability']}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    section("BID DETAIL")
    selected = st.selectbox(
        "Select an opportunity",
        options=df["opportunity_id"].tolist(),
        index=0 if len(df) else None,
        format_func=lambda oid: f"{oid} — {bids[bids.opportunity_id==oid].iloc[0]['project']}",
    )
    if selected:
        b = bids[bids["opportunity_id"] == selected].iloc[0]
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"### {b['project']}")
            st.markdown(
                f"""
                <div style="font-size:13px;color:#64748B;line-height:1.6;">
                  <b>Owner:</b> {b['owner']}<br>
                  <b>Location:</b> {b['location']}<br>
                  <b>Estimated Contract:</b> {money(b['estimated_value'])}<br>
                  <b>Bid Due:</b> {b['bid_due'].strftime('%B %d, %Y')}<br>
                  <b>Probability:</b> {b['probability']}%<br>
                  <b>Estimator:</b> {b['estimator']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            health = min(96, b["probability"] + 15)
            st.markdown(
                f"""
                <div class="ww-card" style="text-align:center;">
                  <div class="ww-kpi-label">BID HEALTH SCORE</div>
                  <div style="font-size:34px;font-weight:700;color:#1D4ED8;
                              margin-top:4px;">{health}<span style="font-size:16px;
                              color:#94A3B8;"> / 100</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="ww-card">
                  <div class="ww-kpi-label">STATUS</div>
                  <div style="margin-top:8px;">{status_badge(b['status'])}</div>
                  <div class="ww-kpi-label" style="margin-top:14px;">SCORE BREAKDOWN</div>
                  <div style="font-size:12.5px;color:#475569;line-height:1.7;margin-top:6px;">
                    Scope clarity: <b>91</b><br>
                    Cost confidence: <b>84</b><br>
                    Schedule confidence: <b>88</b><br>
                    Vendor coverage: <b>82</b>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        section("SCOPE")
        st.markdown(
            """
            - Treatment plant expansion
            - Structural concrete
            - Underground piping
            - Mechanical systems
            - Electrical
            - Site work
            """
        )

        section("KEY DATES")
        st.markdown(
            f"""
            | Milestone | Date |
            |---|---|
            | Bid Documents Received | Aug 12, 2026 |
            | Site Visit | Aug 26, 2026 |
            | Questions Due | Sep 05, 2026 |
            | Bid Submission | **{b['bid_due'].strftime('%b %d, %Y')}** |
            | Expected Award | Oct 30, 2026 |
            """
        )


# ===========================================================================
# PAGE: ESTIMATING
# ===========================================================================
def page_estimating():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">New Project Estimate</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Eastside Wastewater Treatment Expansion · City Water Authority
        </div>
        """,
        unsafe_allow_html=True,
    )

    section("ESTIMATE LINE ITEMS")
    estimate_rows = [
        ("Concrete",   "Structural foundation",  2400,  "CY",    185,  444_000),
        ("Concrete",   "Reinforced walls",        1800,  "CY",    210,  378_000),
        ("Piping",     "Process piping",          8500,  "LF",    74,   629_000),
        ("Piping",     "Underground utilities",   4200,  "LF",    96,   403_200),
        ("Mechanical", "Pumps & motors",          6,     "EA",    145_000, 870_000),
        ("Mechanical", "Valves & actuators",      42,    "EA",    8_200, 344_400),
        ("Electrical", "MCC panels",              8,     "EA",    48_000, 384_000),
        ("Electrical", "Wiring & conduit",        24000, "LF",    22,   528_000),
        ("Equipment",  "Excavators",              1200,  "HR",    165,  198_000),
        ("Equipment",  "Cranes",                  640,   "HR",    285,  182_400),
        ("Labor",      "Installation",            12500, "Hours", 48,   600_000),
        ("Labor",      "Pipefitters",             8200,  "HR",    68,   557_600),
        ("Subcontractors", "Site clearing",       1,     "LS",    145_000, 145_000),
        ("Subcontractors", "Roofing",             1,     "LS",    124_000, 124_000),
        ("Permits",    "Permits & fees",          1,     "LS",    68_000, 68_000),
        ("Overhead",   "General conditions",      1,     "LS",    494_400, 494_400),
        ("Contingency","Project contingency",     1,     "LS",    308_000, 308_000),
    ]
    est_df = pd.DataFrame(estimate_rows,
                          columns=["Category", "Description", "Quantity",
                                   "Unit", "Unit Cost", "Total"])
    st.dataframe(
        est_df, use_container_width=True, hide_index=True, height=460,
        column_config={
            "Unit Cost": st.column_config.NumberColumn(format="$%d"),
            "Total": st.column_config.NumberColumn(format="$%d"),
            "Quantity": st.column_config.NumberColumn(format="%d"),
        },
    )

    section("ESTIMATE SUMMARY")
    direct = 6_180_000
    overhead = 494_400
    contingency = 308_000
    profit = 1_467_600
    contract = 8_450_000
    margin = profit / contract * 100

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1: kpi_card("DIRECT COST", money(direct))
    with s2: kpi_card("OVERHEAD", money(overhead))
    with s3: kpi_card("CONTINGENCY", money(contingency))
    with s4: kpi_card("EXPECTED PROFIT", money(profit), f"{margin:.1f}% margin")
    with s5: kpi_card("PROPOSED CONTRACT", money(contract), "Gross Margin", f"{margin:.1f}%")

    # Margin gauge
    section("MARGIN GAUGE")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=margin,
        number={"suffix": "%", "font": {"size": 40}},
        gauge={
            "axis": {"range": [0, 25], "tickwidth": 1, "tickcolor": "#94A3B8"},
            "bar": {"color": "#1D4ED8"},
            "steps": [
                {"range": [0, 10], "color": "#FEE2E2"},
                {"range": [10, 15], "color": "#FEF3C7"},
                {"range": [15, 25], "color": "#DCFCE7"},
            ],
            "threshold": {
                "line": {"color": "#0F172A", "width": 3},
                "thickness": 0.8, "value": 17.5,
            },
        },
        title={"text": "Gross Margin · Target 17.5%"},
    ))
    plotly_defaults(fig, height=300)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # AI estimate analysis
    section("AI ESTIMATE ANALYSIS")
    if st.button("✦ Analyze Estimate with AI", type="primary"):
        with st.spinner("Analyzing estimate across 2,140 comparable projects…"):
            st.session_state["ai_estimate_result"] = AI.run_estimate_agent(
                "Eastside Wastewater Treatment Expansion",
                direct, overhead, contingency, profit, contract,
            )

    res = st.session_state.get("ai_estimate_result")
    if res:
        st.markdown(
            f"""
            <div class="ww-ai">
              <div class="ww-ai-title">AI ESTIMATE REVIEW</div>
              <div class="ww-ai-body">
                <b>Overall confidence:</b> {res['confidence']} / 100<br><br>
                <b>Findings</b><br>
                {'<br>'.join(f"{'✓' if k=='ok' else '⚠'} {t}" for k, t in res['findings'])}
                <br><br>
                <b>Recommendation</b><br>
                {res['recommendation']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Apply Recommendation (simulated)"):
            st.toast("Recommendation applied — contingency increased by 1.5%.", icon="✅")


# ===========================================================================
# PAGE: QUOTE COMPARISON
# ===========================================================================
def page_quotes():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">
          Subcontractor & Vendor Quote Intelligence</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Eastside Wastewater Treatment Expansion · Mechanical scope
        </div>
        """,
        unsafe_allow_html=True,
    )

    merged = quotes.merge(vendors, on="vendor_id", how="left")
    min_price = merged["price"].min()
    merged["computed_score"] = merged.apply(
        lambda r: A.score_quote(r, min_price), axis=1)

    show = merged[["vendor_name", "price", "scope_coverage", "timeline_weeks",
                   "warranty_years", "payment_terms", "experience",
                   "computed_score"]].copy()
    show.columns = ["Vendor", "Price", "Coverage", "Timeline (wks)",
                    "Warranty (yrs)", "Terms", "Experience", "AI Score"]
    show["Price"] = show["Price"].apply(lambda v: f"${v:,.0f}")
    show["Coverage"] = show["Coverage"].apply(lambda v: f"{v}%")

    st.dataframe(show, use_container_width=True, hide_index=True, height=260)

    section("AI RECOMMENDATION")
    if st.button("✦ Compare Quotes with AI", type="primary"):
        with st.spinner("Scoring quotes across price, coverage, schedule, warranty, terms…"):
            st.session_state["ai_quote_result"] = AI.run_quote_agent(quotes, vendors)

    res = st.session_state.get("ai_quote_result")
    if res:
        b = res["best"]
        st.markdown(
            f"""
            <div class="ww-ai">
              <div class="ww-ai-title">AI RECOMMENDATION</div>
              <div class="ww-ai-body">
                <div style="font-size:22px;font-weight:700;color:#0F172A;">
                  {b['vendor_name']}</div>
                <div style="font-size:13px;color:#1D4ED8;font-weight:600;margin:4px 0 12px 0;">
                  AI Score: {b['computed_score']:.0f} / 100</div>
                <b>Reason</b><br>{res['reason']}<br><br>
                <table style="width:100%;font-size:13px;">
                  <tr>
                    <td style="color:#64748B;">Price Impact</td>
                    <td><b>${res['price_delta']:+,.0f}</b></td>
                    <td style="color:#64748B;">Schedule Advantage</td>
                    <td><b>{res['schedule_advantage']} weeks</b></td>
                  </tr>
                  <tr>
                    <td style="color:#64748B;">Scope Coverage</td>
                    <td><b>+{res['coverage_advantage']}%</b></td>
                    <td style="color:#64748B;">Warranty</td>
                    <td><b>+{res['warranty_advantage']} years</b></td>
                  </tr>
                </table>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Select {b['vendor_name']}", type="primary"):
            st.session_state["quote_selected"] = b["vendor_name"]
            st.toast(f"{b['vendor_name']} selected for mechanical scope.", icon="✅")

    if st.session_state.get("quote_selected"):
        st.success(f"Vendor selected: **{st.session_state['quote_selected']}**")


# ===========================================================================
# PAGE: PROJECTS
# ===========================================================================
def page_projects():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">Projects</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Active portfolio · cost tracking · schedule · change orders · risk.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        st.markdown("**Select a project**")
        pid = st.selectbox(
            "Project",
            options=projects["project_id"].tolist(),
            index=projects["project_id"].tolist().index(st.session_state["selected_project"])
                  if st.session_state["selected_project"] in projects["project_id"].tolist() else 1,
            format_func=lambda p: f"{p} — {projects[projects.project_id==p].iloc[0]['project_name']}",
            label_visibility="collapsed",
        )
        st.session_state["selected_project"] = pid
    with c2:
        status_filter = st.multiselect(
            "Risk Level", options=["Healthy", "Watch", "At Risk", "Critical"],
            default=["Healthy", "Watch", "At Risk", "Critical"])
    with c3:
        sort_by = st.selectbox("Sort by", ["Contract Value", "Margin", "Progress"])

    table = projects.copy()
    table = table[table["risk_level"].isin(status_filter)]
    sort_map = {"Contract Value": "contract_value", "Margin": "expected_margin", "Progress": "progress"}
    table = table.sort_values(sort_map[sort_by], ascending=False)
    show = table[["project_id", "project_name", "contract_value", "actual_cost",
                  "forecast_cost", "projected_profit", "expected_margin",
                  "progress", "risk_level"]].copy()
    show["contract_value"] = show["contract_value"].apply(money)
    show["actual_cost"] = show["actual_cost"].apply(money)
    show["forecast_cost"] = show["forecast_cost"].apply(money)
    show["projected_profit"] = show["projected_profit"].apply(money)
    show["expected_margin"] = show["expected_margin"].apply(lambda v: f"{v:.1f}%")
    show["progress"] = show["progress"].apply(lambda v: f"{v}%")
    show.columns = ["ID", "Project", "Contract", "Actual", "Forecast",
                    "Profit", "Margin", "Progress", "Risk"]
    st.dataframe(show, use_container_width=True, hide_index=True, height=380)

    # Detail
    p = projects[projects["project_id"] == pid].iloc[0]
    section(f"PROJECT DETAIL · {p['project_id']}")
    d1, d2, d3, d4, d5 = st.columns(5)
    with d1: kpi_card("CONTRACT", money(p["contract_value"]))
    with d2: kpi_card("PROGRESS", f"{p['progress']}%")
    with d3: kpi_card("BUDGET", money(p["budget"]))
    with d4: kpi_card("ACTUAL COST", money(p["actual_cost"]))
    with d5: kpi_card("FORECAST COST", money(p["forecast_cost"]))

    d6, d7, d8, d9 = st.columns(4)
    with d6: kpi_card("PROJECTED PROFIT", money(p["projected_profit"]))
    with d7: kpi_card("EXPECTED MARGIN", f"{p['expected_margin']:.1f}%")
    with d8: kpi_card("ORIGINAL MARGIN", f"{p['original_margin']:.1f}%")
    with d9: kpi_card("MARGIN EROSION", f"-{p['margin_erosion']:.1f} pts",
                      trend_class="neg")

    tabs = st.tabs(["Overview", "Financials", "Cost Breakdown",
                    "Change Orders", "Risks", "Activity"])

    with tabs[0]:
        st.markdown(f"**{p['project_name']}**")
        st.markdown(
            f"""
            - **Owner:** {p['owner']}
            - **Location:** {p['location']}
            - **Project Manager:** {p['pm']}
            - **Start Date:** {p['start_date'].strftime('%B %d, %Y')}
            - **Risk Level:** {p['risk_level']}
            """
        )

    with tabs[1]:
        st.plotly_chart(
            plotly_defaults(go.Figure(go.Indicator(
                mode="number+delta",
                value=p["expected_margin"],
                delta={"reference": p["original_margin"], "suffix": " pts"},
                number={"suffix": "%", "font": {"size": 44}},
                title={"text": "Expected Margin vs. Original"},
            )), height=280),
            use_container_width=True, config={"displayModeBar": False})

    with tabs[2]:
        cat = A.cost_by_category(costs, pid)
        if cat.empty:
            st.info("No cost detail for this project.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=cat["category"], y=cat["budget"],
                                 name="Budget", marker_color="#CBD5E1"))
            fig.add_trace(go.Bar(x=cat["category"], y=cat["actual"],
                                 name="Actual", marker_color="#1D4ED8"))
            fig.add_trace(go.Bar(x=cat["category"], y=cat["forecast"],
                                 name="Forecast", marker_color="#93C5FD"))
            fig.update_layout(barmode="group", yaxis_title="USD")
            plotly_defaults(fig, height=340)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            styled = cat.copy()
            styled["budget"] = styled["budget"].apply(money)
            styled["actual"] = styled["actual"].apply(money)
            styled["forecast"] = styled["forecast"].apply(money)
            styled["variance"] = styled["variance"].apply(
                lambda v: f"{'+' if v>=0 else ''}{money(v)}")
            styled["variance_pct"] = styled["variance_pct"].apply(lambda v: f"{v:+.1f}%")
            styled.columns = ["Category", "Budget", "Actual", "Forecast", "Variance", "Var %"]
            st.dataframe(styled, use_container_width=True, hide_index=True)

            st.markdown(
                f"""
                <div class="ww-ai">
                  <div class="ww-ai-title">AI COST ANALYSIS</div>
                  <div class="ww-ai-body">
                    {AI.run_project_agent(p, cat).replace(chr(10), '<br>')}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tabs[3]:
        pcos = cos[cos["project_id"] == pid]
        if pcos.empty:
            st.info("No change orders for this project.")
        else:
            show = pcos[["co_id", "description", "requested_amount", "cost",
                         "potential_profit", "margin_pct", "status", "days_pending"]].copy()
            show["requested_amount"] = show["requested_amount"].apply(money)
            show["cost"] = show["cost"].apply(money)
            show["potential_profit"] = show["potential_profit"].apply(money)
            show["margin_pct"] = show["margin_pct"].apply(lambda v: f"{v:.1f}%")
            show.columns = ["CO", "Description", "Requested", "Cost",
                            "Profit", "Margin", "Status", "Days"]
            st.dataframe(show, use_container_width=True, hide_index=True)

    with tabs[4]:
        prisk = [r for r in risks if r["project_id"] == pid]
        if not prisk:
            st.success("No material risks detected.")
        for r in prisk:
            sev_class = {"Critical": "crit", "High": "high",
                         "Medium": "med"}.get(r["severity"], "low")
            st.markdown(
                f"""
                <div class="ww-risk {sev_class}">
                  <div style="font-size:11px;color:#64748B;font-weight:700;
                              letter-spacing:0.6px;">{r['severity'].upper()} · {r['category']}</div>
                  <div style="font-size:14px;font-weight:600;color:#0F172A;margin-top:6px;">
                    {r['detail']}</div>
                  <div style="font-size:13px;color:#475569;margin-top:6px;">
                    Potential impact: <b>{money(r['impact'])}</b></div>
                  <div style="font-size:12.5px;color:#64748B;margin-top:4px;">
                    Cause: {r['cause']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tabs[5]:
        st.markdown(
            f"""
            - **Aug 24, 2026 · 09:12** — Cost report received from field
            - **Aug 22, 2026 · 16:40** — Change order CO-1048 submitted for review
            - **Aug 19, 2026 · 11:05** — Vendor quote Q-5003 received (Cascade Industrial)
            - **Aug 15, 2026 · 14:22** — Monthly pay application approved
            - **Aug 12, 2026 · 10:01** — Safety walk completed, no findings
            """
        )


# ===========================================================================
# PAGE: CHANGE ORDERS
# ===========================================================================
def page_change_orders():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">Change Orders</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Pending, under review, and approved change orders across the portfolio.
        </div>
        """,
        unsafe_allow_html=True,
    )

    pending = cos[cos["status"].isin(["Pending Approval", "Under Review", "Submitted"])]
    approved_month = cos[cos["status"] == "Approved"]["requested_amount"].sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("PENDING CHANGE ORDERS", str(len(pending)))
    with c2: kpi_card("PENDING VALUE", money(pending["requested_amount"].sum()))
    with c3: kpi_card("APPROVED THIS MONTH", money(approved_month))
    with c4: kpi_card("AVG DAYS PENDING",
                      f"{pending['days_pending'].mean():.0f} days")

    stages = ["Draft", "Submitted", "Under Review", "Approved", "Rejected"]
    section("PIPELINE")
    counts = {
        "Draft": 0,
        "Submitted": len(cos[cos["status"] == "Submitted"]),
        "Under Review": len(cos[cos["status"] == "Under Review"]),
        "Approved": len(cos[cos["status"] == "Approved"]),
        "Rejected": len(cos[cos["status"] == "Rejected"]),
    }
    cols = st.columns(5)
    for (stage, count), col in zip(counts.items(), cols):
        with col:
            st.markdown(
                f"""
                <div class="ww-card" style="text-align:center;padding:14px;">
                  <div class="ww-kpi-label">{stage.upper()}</div>
                  <div style="font-size:26px;font-weight:700;color:#0F172A;
                              margin-top:4px;">{count}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    section("ALL CHANGE ORDERS")
    show = cos.copy()
    show["requested_amount"] = show["requested_amount"].apply(money)
    show["cost"] = show["cost"].apply(money)
    show["potential_profit"] = show["potential_profit"].apply(money)
    show["margin_pct"] = show["margin_pct"].apply(lambda v: f"{v:.1f}%")
    show = show[["co_id", "project_id", "description", "requested_amount", "cost",
                 "potential_profit", "margin_pct", "status", "days_pending", "owner"]]
    show.columns = ["CO", "Project", "Description", "Requested", "Cost",
                    "Profit", "Margin", "Status", "Days", "Owner"]
    st.dataframe(show, use_container_width=True, hide_index=True, height=420)

    # CO detail
    section("CHANGE ORDER DETAIL · CO-1048")
    co = cos[cos["co_id"] == "CO-1048"].iloc[0]
    d1, d2, d3, d4 = st.columns(4)
    with d1: kpi_card("REQUESTED", money(co["requested_amount"]))
    with d2: kpi_card("COST", money(co["cost"]))
    with d3: kpi_card("POTENTIAL PROFIT", money(co["potential_profit"]),
                      f"{co['margin_pct']:.1f}% margin")
    with d4: kpi_card("STATUS", co["status"], f"{int(co['days_pending'])} days pending",
                      trend_class="warn")

    st.markdown(
        f"""
        <div style="font-size:13px;color:#475569;margin-top:8px;">
          <b>Project:</b> {co['project_id']} — Eastside Wastewater Expansion<br>
          <b>Description:</b> {co['description']}<br>
          <b>Submitted:</b> {co['submitted_date']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("✦ Analyze Change Order", type="primary", use_container_width=True):
            st.session_state["ai_co_result"] = {
                "analysis": ("Change Order CO-1048 appears commercially favorable if "
                             "approved. Estimated gross margin is 32.4%. However, the "
                             "proposed completion extension should be clarified before "
                             "submission."),
                "recs": ["Verify labor assumptions",
                         "Confirm schedule impact",
                         "Attach supporting scope documentation"],
            }
    with colB:
        if co["co_id"] not in st.session_state["co_approved"]:
            if st.button("Approve Change Order", use_container_width=True):
                st.session_state["co_approved"].add(co["co_id"])
                st.toast(f"{co['co_id']} approved.", icon="✅")
                st.rerun()
        else:
            st.success("✓ Approved")

    res = st.session_state.get("ai_co_result")
    if res:
        st.markdown(
            f"""
            <div class="ww-ai">
              <div class="ww-ai-title">AI CHANGE ORDER ANALYSIS</div>
              <div class="ww-ai-body">
                {res['analysis']}<br><br>
                <b>Recommendations</b><br>
                {'<br>'.join('✓ ' + r for r in res['recs'])}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ===========================================================================
# PAGE: FINANCIALS
# ===========================================================================
def page_financials():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">Financials</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Executive view of revenue, cost, profit, and receivables across the portfolio.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("CONTRACT REVENUE", money(fin["contract_revenue"]))
    with c2: kpi_card("ACTUAL COST", money(fin["actual_cost"]))
    with c3: kpi_card("FORECAST COST", money(fin["forecast_cost"]))
    c4, c5, c6 = st.columns(3)
    with c4: kpi_card("PROJECTED PROFIT", money(fin["projected_profit"]),
                      f"{fin['projected_profit']/fin['contract_revenue']*100:.1f}% margin")
    with c5: kpi_card("COLLECTED", money(fin["collected"]))
    with c6: kpi_card("OUTSTANDING", money(fin["outstanding"]), trend_class="warn")

    section("REVENUE VS COST")
    rc = A.monthly_revenue_cost(projects)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rc["month"], y=rc["revenue"], name="Revenue",
                             mode="lines", fill="tozeroy",
                             line=dict(color="#1D4ED8", width=2),
                             fillcolor="rgba(29,78,216,0.10)"))
    fig.add_trace(go.Scatter(x=rc["month"], y=rc["cost"], name="Cost",
                             mode="lines", fill="tozeroy",
                             line=dict(color="#94A3B8", width=2),
                             fillcolor="rgba(148,163,184,0.15)"))
    plotly_defaults(fig, height=320)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    colA, colB = st.columns(2)
    with colA:
        section("BUDGET VS ACTUAL BY PROJECT")
        p = A.profitability_frame(projects).sort_values("contract_value", ascending=False).head(8)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=p["project_id"], y=p["budget"], name="Budget",
                              marker_color="#CBD5E1"))
        fig2.add_trace(go.Bar(x=p["project_id"], y=p["actual_cost"], name="Actual",
                              marker_color="#1D4ED8"))
        fig2.update_layout(barmode="group")
        plotly_defaults(fig2, height=320)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with colB:
        section("PROFIT MARGIN BY PROJECT")
        p = A.profitability_frame(projects).sort_values("Margin %", ascending=False)
        fig3 = go.Figure(go.Bar(
            x=p["Margin %"], y=p["project_id"], orientation="h",
            marker_color=["#16A34A" if m >= 15 else "#D97706" if m >= 12 else "#DC2626"
                          for m in p["Margin %"]],
            text=[f"{m:.1f}%" for m in p["Margin %"]],
            textposition="outside",
        ))
        fig3.update_xaxes(title_text="Gross Margin %")
        plotly_defaults(fig3, height=320)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    section("OUTSTANDING RECEIVABLES")
    ar = txns[(txns["type"] == "Receivable") &
              (txns["status"].isin(["Pending", "Overdue"]))].copy()
    ar = ar.sort_values("amount", ascending=False).head(10)
    show = ar[["reference", "project_id", "amount", "status", "date"]].copy()
    show["amount"] = show["amount"].apply(money)
    show["date"] = show["date"].dt.strftime("%b %d, %Y")
    show.columns = ["Reference", "Project", "Amount", "Status", "Date"]
    st.dataframe(show, use_container_width=True, hide_index=True)

    section("CASH FLOW FORECAST")
    months = pd.date_range("2026-08-01", periods=6, freq="MS")
    inflow = np.array([3.2, 3.8, 4.1, 4.4, 4.0, 3.6]) * 1e6
    outflow = np.array([2.6, 3.0, 3.3, 3.4, 3.2, 2.9]) * 1e6
    net = inflow - outflow
    cum = np.cumsum(net)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=months, y=inflow, name="Inflow", marker_color="#1D4ED8"))
    fig4.add_trace(go.Bar(x=months, y=-outflow, name="Outflow", marker_color="#94A3B8"))
    fig4.add_trace(go.Scatter(x=months, y=cum, name="Cumulative",
                              mode="lines+markers",
                              line=dict(color="#16A34A", width=2)))
    plotly_defaults(fig4, height=320)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# PAGE: RISK CENTER
# ===========================================================================
def page_risk():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">AI Project Risk Center</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          AI continuously scans project data for financial and operational risks.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 2.6])
    with left:
        st.markdown(
            f"""
            <div class="ww-card" style="text-align:center;">
              <div class="ww-kpi-label">OVERALL PORTFOLIO RISK</div>
              <div style="font-size:44px;font-weight:700;
                          color:{'#DC2626' if risk_score>=80 else '#D97706' if risk_score>=60 else '#16A34A' if risk_score<35 else '#CA8A04'};
                          margin:6px 0 2px 0;">{risk_score}<span style="font-size:16px;color:#94A3B8;"> / 100</span></div>
              <div style="font-size:13px;font-weight:600;color:#475569;">{risk_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        section("RISK BREAKDOWN")
        sev_counts = pd.Series([r["severity"] for r in risks]).value_counts()
        for sev in ["Critical", "High", "Medium", "Low"]:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:6px 0;font-size:13px;">'
                f'<span>{risk_badge(sev)}</span>'
                f'<b>{int(sev_counts.get(sev, 0))}</b></div>',
                unsafe_allow_html=True,
            )

    with right:
        section("RISK CARDS")
        order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        risks_sorted = sorted(risks, key=lambda r: order.get(r["severity"], 4))
        if not risks_sorted:
            st.success("No material risks detected.")
        for r in risks_sorted[:8]:
            sev_class = {"Critical": "crit", "High": "high",
                         "Medium": "med"}.get(r["severity"], "low")
            st.markdown(
                f"""
                <div class="ww-risk {sev_class}">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:11px;color:#64748B;font-weight:700;
                                letter-spacing:0.6px;">{risk_badge(r['severity'])}
                                &nbsp;&nbsp;{r['category'].upper()}</div>
                    <div style="font-size:13px;font-weight:700;color:#0F172A;">
                      {r['project_id']}</div>
                  </div>
                  <div style="font-size:14.5px;font-weight:600;color:#0F172A;margin-top:8px;">
                    {r['project_name'] if r['project_name'] != '—' else r['category']}</div>
                  <div style="font-size:13px;color:#475569;margin-top:4px;">{r['detail']}</div>
                  <div style="font-size:13px;color:#475569;margin-top:8px;">
                    Potential impact: <b style="color:#B91C1C;">{money(r['impact'])}</b>
                    &nbsp;·&nbsp; Cause: {r['cause']}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Investigate {r['project_id']}", key=f"inv_{r['project_id']}_{r['category']}"):
                st.session_state["selected_project"] = r["project_id"]
                st.session_state["page"] = "Projects"
                st.rerun()

    section("AI RISK NARRATIVE")
    st.markdown(
        f"""
        <div class="ww-ai">
          <div class="ww-ai-title">AI PORTFOLIO RISK BRIEF</div>
          <div class="ww-ai-body">
            {AI.run_risk_agent(risks).replace(chr(10), '<br>')}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# PAGE: AI ASSISTANT (Decision Center)
# ===========================================================================
def page_ai():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">
          WaterWorks AI Decision Center</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Ask questions about your projects, bids and financial performance.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section("SUGGESTED QUESTIONS")
    cols = st.columns(4)
    for i, q in enumerate(AI.SUGGESTED_QUESTIONS):
        with cols[i % 4]:
            if st.button(q, use_container_width=True, key=f"sugg_{i}"):
                st.session_state["_pending_question"] = q
                st.rerun()

    section("ASK WATERWORKS AI")
    question = st.text_input(
        "Question",
        value=st.session_state.pop("_pending_question", ""),
        placeholder="e.g. What should management focus on today?",
        label_visibility="collapsed",
    )

    if question:
        with st.spinner("Analyzing portfolio…"):
            ans = AI.answer_question(
                question, projects, bids, cos, txns, costs, quotes, vendors
            )

        st.markdown(
            f"""
            <div class="ww-ai">
              <div class="ww-ai-title">WATERWORKS AI · RESPONSE</div>
              <div class="ww-ai-body" style="font-size:15px;font-weight:600;">
                {ans['summary']}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if ans["cards"]:
            ncols = min(len(ans["cards"]), 4)
            cols = st.columns(ncols)
            for card, col in zip(ans["cards"], cols):
                with col:
                    st.markdown(
                        f"""
                        <div class="ww-card" style="padding:14px;">
                          <div style="font-size:11px;color:#64748B;font-weight:700;
                                      letter-spacing:0.5px;">{card['id']}</div>
                          <div style="font-size:13.5px;font-weight:600;color:#0F172A;
                                      margin:6px 0;">{card['title']}</div>
                          <div style="font-size:13px;color:#1D4ED8;font-weight:700;">
                            {card['margin']}</div>
                          <div style="margin-top:6px;">{risk_badge(card['risk'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown(
            f"""
            <div style="margin-top:14px;font-size:14px;color:#1E293B;line-height:1.65;">
              <b>Explanation.</b> {ans['explanation']}<br><br>
              <b>Evidence.</b> {ans.get('evidence') or '—'}<br><br>
              <b>Recommendation.</b> {ans.get('recommendation') or '—'}<br><br>
              <b>Estimated financial impact.</b>
              <span style="color:{'#B91C1C' if ans['impact']<0 else '#15803D'};font-weight:700;">
                {money(ans['impact'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="margin-top:22px;font-size:11.5px;color:#94A3B8;">
          AI provider: <b>{AI.provider()}</b> ·
          Set <code>GROQ_API_KEY</code> in environment or Streamlit secrets to enable live AI.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# PAGE: SETTINGS
# ===========================================================================
def page_settings():
    st.markdown(
        """
        <div style="font-size:22px;font-weight:700;color:#0F172A;">Settings</div>
        <div style="font-size:13.5px;color:#64748B;margin-bottom:14px;">
          Workspace configuration, data upload, and diagnostics.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Workspace", "Upload Project Data", "Diagnostics"])

    with tabs[0]:
        st.markdown(
            """
            **Workspace** · Demo Workspace  
            **Industry** · Water & Wastewater Infrastructure  
            **Region** · Pacific Northwest, USA  
            **AI Provider** · """ + AI.provider().upper() + """  
            """
        )
        st.info("This is a demo workspace. No data leaves your browser session.")

    with tabs[1]:
        st.markdown(
            "Upload a CSV or XLSX file containing your own project or cost data. "
            "Original data is never modified."
        )
        file = st.file_uploader("Upload project data", type=["csv", "xlsx"])
        if file is not None:
            try:
                if file.name.lower().endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file, engine="openpyxl")
                st.session_state["uploaded_df"] = df
                st.success(f"Loaded {len(df):,} rows × {len(df.columns)} columns.")
                st.markdown("**Preview**")
                st.dataframe(df.head(20), use_container_width=True)
                st.markdown("**Column summary**")
                summary = pd.DataFrame({
                    "dtype": df.dtypes.astype(str),
                    "non_null": df.notna().sum(),
                    "unique": df.nunique(),
                })
                st.dataframe(summary, use_container_width=True)
                num = df.select_dtypes(include=[np.number])
                if not num.empty:
                    st.markdown("**Numeric statistics**")
                    st.dataframe(num.describe().T, use_container_width=True)
            except Exception as e:
                st.error(f"Could not parse file: {e}")

    with tabs[2]:
        st.markdown("**Data diagnostics**")
        diag = pd.DataFrame({
            "Dataset": ["Projects", "Bids", "Vendors", "Quotes",
                        "Costs", "Change Orders", "Transactions"],
            "Rows": [len(projects), len(bids), len(vendors), len(quotes),
                     len(costs), len(cos), len(txns)],
            "Columns": [projects.shape[1], bids.shape[1], vendors.shape[1],
                        quotes.shape[1], costs.shape[1], cos.shape[1], txns.shape[1]],
        })
        st.dataframe(diag, use_container_width=True, hide_index=True)
        st.markdown(
            f"""
            - Portfolio risk score: **{risk_score}/100 ({risk_label})**
            - Total risks detected: **{len(risks)}**
            - AI provider: **{AI.provider()}**
            """
        )
        if st.button("Reload demo data (clears cache)"):
            st.cache_data.clear()
            st.success("Cache cleared. Reload the page to see fresh data.")


# ===========================================================================
# ROUTER
# ===========================================================================
router = {
    "Executive Dashboard": page_dashboard,
    "Bid Opportunities": page_bids,
    "Estimating": page_estimating,
    "Quote Comparison": page_quotes,
    "Projects": page_projects,
    "Change Orders": page_change_orders,
    "Financials": page_financials,
    "Risk Center": page_risk,
    "AI Assistant": page_ai,
    "Settings": page_settings,
}
router.get(st.session_state["page"], page_dashboard)()
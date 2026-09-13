"""ReportLab executive PDF report."""
from __future__ import annotations
import io
from datetime import datetime
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


NAVY = colors.HexColor("#0F172A")
BLUE = colors.HexColor("#1D4ED8")
GRAY = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#E2E8F0")


def _money(v):
    try:
        return f"${float(v)/1e6:.2f}M"
    except Exception:
        return "—"


def build_report(kpis: dict,
                 fin: dict,
                 projects: pd.DataFrame,
                 risks: list[dict],
                 cos: pd.DataFrame,
                 risk_score: int,
                 risk_label: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        title="WaterWorks AI — Executive Report",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=20,
                        textColor=NAVY, spaceAfter=4, leading=24)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13,
                        textColor=BLUE, spaceBefore=14, spaceAfter=6, leading=16)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10,
                          textColor=NAVY, leading=14)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=9,
                           textColor=GRAY, leading=12)

    story = []
    story.append(Paragraph("WaterWorks AI", h1))
    story.append(Paragraph("Executive Portfolio Report", h2))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y · %H:%M')} · Demo Workspace", small))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Portfolio KPIs", h2))
    story.append(_table([
        ["Metric", "Value"],
        ["Active Projects", str(kpis["active_projects"])],
        ["Backlog", _money(kpis["backlog"])],
        ["Weighted Pipeline", _money(kpis["pipeline"])],
        ["Projected Profit", _money(kpis["projected_profit"])],
        ["At-Risk Value", _money(kpis["at_risk_value"])],
        ["Outstanding Receivables", _money(kpis["outstanding"])],
    ]))

    story.append(Paragraph("Financial Summary", h2))
    story.append(_table([
        ["Metric", "Value"],
        ["Contract Revenue", _money(fin["contract_revenue"])],
        ["Actual Cost to Date", _money(fin["actual_cost"])],
        ["Forecast Cost at Completion", _money(fin["forecast_cost"])],
        ["Projected Profit", _money(fin["projected_profit"])],
        ["Collected", _money(fin["collected"])],
        ["Outstanding", _money(fin["outstanding"])],
    ]))

    story.append(PageBreak())

    story.append(Paragraph("Project Status", h2))
    rows = [["Project ID", "Project", "Contract", "Forecast", "Margin", "Risk"]]
    for _, p in projects.sort_values("contract_value", ascending=False).head(12).iterrows():
        rows.append([
            p["project_id"], _truncate(p["project_name"], 34),
            _money(p["contract_value"]), _money(p["forecast_cost"]),
            f"{p['expected_margin']:.1f}%", p["risk_level"],
        ])
    story.append(_table(rows, col_widths=[0.8*inch, 2.3*inch, 0.9*inch, 0.9*inch, 0.7*inch, 0.7*inch]))

    story.append(Paragraph(f"Risk Analysis — Portfolio Score {risk_score}/100 ({risk_label})", h2))
    if risks:
        rows = [["Severity", "Project", "Category", "Detail", "Impact"]]
        for r in risks[:10]:
            rows.append([
                r["severity"], r["project_id"], r["category"],
                _truncate(r["detail"], 40), f"{r['impact']:+,.0f}",
            ])
        story.append(_table(rows, col_widths=[0.8*inch, 0.9*inch, 1.2*inch, 2.3*inch, 0.9*inch]))
    else:
        story.append(Paragraph("No material risks detected.", body))

    story.append(Paragraph("Change Orders", h2))
    pending = cos[cos["status"].isin(["Pending Approval", "Under Review", "Submitted"])]
    rows = [["CO", "Project", "Description", "Requested", "Margin", "Days"]]
    for _, c in pending.iterrows():
        rows.append([
            c["co_id"], c["project_id"], _truncate(c["description"], 32),
            f"${c['requested_amount']:,.0f}", f"{c['margin_pct']:.1f}%",
            str(int(c["days_pending"])),
        ])
    story.append(_table(rows, col_widths=[0.8*inch, 0.9*inch, 2.3*inch, 1.0*inch, 0.7*inch, 0.5*inch]))

    story.append(Paragraph("AI Recommendations", h2))
    recs = [
        "Re-baseline WW-24018 forecast; equipment and material costs are trending above budget.",
        "Escalate CO-1048 to owner review — 12 days pending, $284K exposure.",
        "Collect on WW-24011 overdue receivable ($420K, 29 days).",
        "Award mechanical scope to Cascade Industrial — best total-value proposal.",
    ]
    for r in recs:
        story.append(Paragraph(f"• {r}", body))

    doc.build(story)
    return buf.getvalue()


def _table(rows, col_widths=None) -> Table:
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _truncate(s: str, n: int) -> str:
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "…"
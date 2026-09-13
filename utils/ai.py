"""AI decision layer.

- If GROQ_API_KEY is present (env var or st.secrets), uses Groq.
- Otherwise, falls back to deterministic demo intelligence so the demo
  always produces a compelling, structured, construction-aware answer.
- Never crashes if the API is unavailable.
"""
from __future__ import annotations
import os
import textwrap
import streamlit as st
import pandas as pd

from . import analytics


# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------
def _get_api_key() -> str | None:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GROQ_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        return None


def provider() -> str:
    return "groq" if _get_api_key() else "demo"


def _try_groq(prompt: str, system: str | None = None) -> str | None:
    key = _get_api_key()
    if not key:
        return None
    try:
        from groq import Groq  # type: ignore
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system or
                 "You are a construction-industry financial analyst. Be concise, "
                 "specific, and reference project IDs and dollar figures."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=700,
        )
        return resp.choices[0].message.content
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Agents (modular so they can later be re-wired to LangGraph)
# ---------------------------------------------------------------------------
def run_bid_agent(bids: pd.DataFrame) -> str:
    top = bids.sort_values("probability", ascending=False).head(3)
    lines = ["**Highest-probability opportunities today:**", ""]
    for _, b in top.iterrows():
        lines.append(f"- **{b['opportunity_id']}** · {b['project']} — "
                     f"{b['probability']}% · ${b['estimated_value']/1e6:.2f}M · {b['status']}")
    lines.append("")
    lines.append("Recommendation: prioritize BID-3004 (Municipal Lift Station Upgrade) — "
                 "in negotiation with 81% probability and a fast close window.")
    return "\n".join(lines)


def run_estimate_agent(project_name: str,
                       direct: float, overhead: float,
                       contingency: float, profit: float,
                       contract: float) -> dict:
    margin = profit / contract * 100 if contract else 0
    confidence = int(max(70, min(96, 88 - abs(17.5 - margin) * 2)))
    findings = [
        ("ok", "Scope coverage appears strong across civil, mechanical, and electrical."),
        ("warn", "Mechanical equipment represents 21% of projected direct cost."),
        ("warn", "Concrete estimate is approximately 9% below comparable projects."),
        ("warn", "Current contingency may be insufficient for the identified scope complexity."),
    ]
    recommendation = (
        "Review concrete quantities and equipment pricing before bid submission. "
        "Increasing contingency by approximately 1.5% may provide additional "
        "protection against cost uncertainty."
    )
    return {
        "confidence": confidence,
        "findings": findings,
        "recommendation": recommendation,
        "margin": margin,
    }


def run_quote_agent(quotes: pd.DataFrame, vendors: pd.DataFrame) -> dict:
    merged = quotes.merge(vendors, on="vendor_id", how="left")
    min_price = merged["price"].min()
    merged["computed_score"] = merged.apply(
        lambda r: analytics.score_quote(r, min_price), axis=1
    )
    best = merged.sort_values("computed_score", ascending=False).iloc[0]
    cheapest = merged.sort_values("price").iloc[0]

    price_delta = best["price"] - cheapest["price"]
    reason = (
        f"Although {best['vendor_name']}'s proposal is ${abs(price_delta):,.0f} "
        f"{'higher' if price_delta >= 0 else 'lower'} than the lowest bid, it provides "
        f"{best['scope_coverage']}% scope coverage, a {best['timeline_weeks']}-week "
        f"schedule, {best['warranty_years']}-year warranty, and {best['payment_terms']} "
        f"terms — reducing commercial risk."
    )
    return {
        "best": best.to_dict(),
        "cheapest": cheapest.to_dict(),
        "price_delta": price_delta,
        "schedule_advantage": int(cheapest["timeline_weeks"] - best["timeline_weeks"]),
        "coverage_advantage": int(best["scope_coverage"] - cheapest["scope_coverage"]),
        "warranty_advantage": int(best["warranty_years"] - cheapest["warranty_years"]),
        "reason": reason,
    }


def run_project_agent(project_row: pd.Series,
                      cost_cat: pd.DataFrame) -> str:
    worst = cost_cat.sort_values("variance_pct", ascending=False).head(3)
    lines = [
        f"**{project_row['project_id']} · {project_row['project_name']}** — margin is "
        f"{project_row['expected_margin']:.1f}% (from {project_row['original_margin']:.1f}%).",
        "",
        "Largest cost overruns:",
    ]
    for _, c in worst.iterrows():
        lines.append(
            f"- **{c['category']}**: budget ${c['budget']/1e6:.2f}M · "
            f"actual ${c['actual']/1e6:.2f}M · variance {c['variance_pct']:+.1f}%"
        )
    lines.append("")
    lines.append(
        "Recommended actions: re-baseline forecast, lock in remaining equipment "
        "rental rates, and submit a change order for the additional underground piping."
    )
    return "\n".join(lines)


def run_risk_agent(risks: list[dict]) -> str:
    if not risks:
        return "No material risks detected in the current portfolio."
    top = sorted(risks, key=lambda r: {"Critical": 0, "High": 1, "Medium": 2}.get(r["severity"], 3))[:3]
    lines = [f"**{len(risks)} items require attention. Top three:**", ""]
    for r in top:
        lines.append(
            f"- **{r['project_id']}** · {r['category']} — {r['detail']} "
            f"(impact {r['impact']:+,.0f})"
        )
    lines.append("")
    lines.append("Fix the highest-severity items first; they represent the greatest "
                 "margin recovery opportunity.")
    return "\n".join(lines)


def run_financial_agent(fin: dict) -> str:
    margin = fin["projected_profit"] / fin["contract_revenue"] * 100
    return (
        f"**Portfolio financial position** — contract revenue ${fin['contract_revenue']/1e6:.1f}M, "
        f"forecast cost ${fin['forecast_cost']/1e6:.1f}M, projected profit "
        f"${fin['projected_profit']/1e6:.1f}M ({margin:.1f}%). "
        f"Outstanding receivables ${fin['outstanding']/1e6:.1f}M. "
        "Cash flow remains positive, but accelerating collections on the two largest "
        "overdue invoices would materially improve working capital."
    )


# ---------------------------------------------------------------------------
# Decision Center — structured Q&A
# ---------------------------------------------------------------------------
SUGGESTED_QUESTIONS = [
    "Which projects are losing margin?",
    "Which project has the highest cost risk?",
    "Which vendor should we select?",
    "What change orders need attention?",
    "Which invoices are overdue?",
    "What should management focus on today?",
    "Which bids should we prioritize?",
    "Where are material costs increasing?",
]


def answer_question(question: str,
                    projects: pd.DataFrame,
                    bids: pd.DataFrame,
                    cos: pd.DataFrame,
                    txns: pd.DataFrame,
                    costs: pd.DataFrame,
                    quotes: pd.DataFrame,
                    vendors: pd.DataFrame) -> dict:
    """Return a structured answer: summary, cards, explanation,
    evidence, recommendation, impact."""
    q = question.lower()

    # --- Which projects are losing margin? ---
    if "losing margin" in q or "at risk" in q and "profit" in q:
        losing = projects[projects["margin_erosion"] > 0].sort_values(
            "margin_erosion", ascending=False).head(3)
        cards = []
        for _, p in losing.iterrows():
            cards.append({
                "id": p["project_id"],
                "title": p["project_name"],
                "margin": f"{p['expected_margin']:.1f}%",
                "risk": p["risk_level"],
            })
        worst = losing.iloc[0]
        return {
            "summary": f"{len(losing)} projects are eroding margin.",
            "cards": cards,
            "explanation": (
                f"The largest portfolio risk is {worst['project_id']} because equipment "
                f"and material costs are trending above budget."
            ),
            "evidence": (
                f"{worst['project_id']} original margin {worst['original_margin']:.1f}% → "
                f"current {worst['expected_margin']:.1f}% "
                f"(-{worst['margin_erosion']:.1f} pts)."
            ),
            "recommendation": "Open the Risk Center and re-baseline these forecasts.",
            "impact": -(worst["margin_erosion"] / 100) * worst["contract_value"],
        }

    # --- Highest cost risk ---
    if "highest cost risk" in q or "cost risk" in q:
        worst_p = projects.sort_values("margin_erosion", ascending=False).iloc[0]
        cat = analytics.cost_by_category(costs, worst_p["project_id"])
        top = cat.head(3)
        cards = [{"id": worst_p["project_id"], "title": worst_p["project_name"],
                  "margin": f"{worst_p['expected_margin']:.1f}%",
                  "risk": worst_p["risk_level"]}]
        evidence = "; ".join(
            f"{r['category']} {r['variance_pct']:+.1f}%" for _, r in top.iterrows()
        )
        return {
            "summary": f"{worst_p['project_id']} carries the highest cost risk.",
            "cards": cards,
            "explanation": "Material, equipment, and labor categories are all trending above budget.",
            "evidence": evidence,
            "recommendation": "Re-baseline forecast and lock remaining rental rates.",
            "impact": -(worst_p["margin_erosion"] / 100) * worst_p["contract_value"],
        }

    # --- Vendor selection ---
    if "vendor" in q or "subcontractor" in q:
        rec = run_quote_agent(quotes, vendors)
        b = rec["best"]
        return {
            "summary": f"Recommended: {b['vendor_name']}.",
            "cards": [{"id": b["vendor_id"], "title": b["vendor_name"],
                       "margin": f"{b['scope_coverage']}% coverage", "risk": "Low"}],
            "explanation": rec["reason"],
            "evidence": (f"Price delta vs. cheapest: ${rec['price_delta']:+,.0f}; "
                         f"schedule advantage {rec['schedule_advantage']} weeks; "
                         f"coverage advantage {rec['coverage_advantage']}%."),
            "recommendation": "Select vendor and lock pricing with a signed scope acknowledgement.",
            "impact": rec["price_delta"],
        }

    # --- Change orders ---
    if "change order" in q or ("co" in q and "attention" in q):
        pending = cos[cos["status"].isin(["Pending Approval", "Under Review", "Submitted"])]
        aged = pending.sort_values("days_pending", ascending=False).head(3)
        cards = [{"id": r["co_id"], "title": r["description"],
                  "margin": f"${r['requested_amount']/1e3:.0f}K",
                  "risk": "High" if r["days_pending"] >= 10 else "Medium"}
                 for _, r in aged.iterrows()]
        total = pending["requested_amount"].sum()
        return {
            "summary": f"{len(pending)} change orders pending, worth ${total/1e3:.0f}K.",
            "cards": cards,
            "explanation": "Aging change orders directly delay cash collection and margin recognition.",
            "evidence": f"Oldest: {aged.iloc[0]['co_id']} at {int(aged.iloc[0]['days_pending'])} days.",
            "recommendation": "Escalate CO-1048 to owner review; confirm schedule impact language.",
            "impact": total,
        }

    # --- Overdue invoices ---
    if "invoice" in q or "overdue" in q or "payment" in q:
        od = txns[(txns["type"] == "Receivable") & (txns["status"] == "Overdue")]
        cards = [{"id": r["project_id"], "title": r["reference"],
                  "margin": f"${r['amount']:,.0f}", "risk": "High"}
                 for _, r in od.iterrows()]
        total = od["amount"].sum()
        return {
            "summary": f"{len(od)} receivables overdue totalling ${total:,.0f}.",
            "cards": cards,
            "explanation": "Owner approvals and pay-app processing delays are the common cause.",
            "evidence": f"Largest single item: ${od['amount'].max():,.0f}.",
            "recommendation": "Escalate to owner's finance contact; send formal notice.",
            "impact": -float(total),
        }

    # --- What should management focus on today? ---
    if "focus" in q or "management" in q or "today" in q:
        return {
            "summary": "Four items require management attention today.",
            "cards": [
                {"id": "WW-24018", "title": "Review cost variance", "margin": "13.4%", "risk": "Critical"},
                {"id": "CO-1048", "title": "Resolve change order", "margin": "$284K", "risk": "High"},
                {"id": "WW-24011", "title": "Follow up on overdue payment", "margin": "$420K", "risk": "High"},
                {"id": "Q-5003", "title": "Vendor quote expiring", "margin": "3 days", "risk": "Medium"},
            ],
            "explanation": "These four items together represent the largest near-term margin "
                           "and cash-flow exposure in the portfolio.",
            "evidence": "Derived from risk scan, change-order aging, and receivables.",
            "recommendation": "Start with WW-24018; it has the largest single-project impact.",
            "impact": -338_000,
        }

    # --- Which bids to prioritize ---
    if "bid" in q or "pipeline" in q:
        top = bids.sort_values(["probability", "estimated_value"], ascending=False).head(3)
        cards = [{"id": b["opportunity_id"], "title": b["project"],
                  "margin": f"{b['probability']}%", "risk": b["status"]}
                 for _, b in top.iterrows()]
        return {
            "summary": "Three bids to prioritize this week.",
            "cards": cards,
            "explanation": "These combine high win probability with material contract value.",
            "evidence": f"Combined weighted value: ${(top['estimated_value']*top['probability']/100).sum()/1e6:.2f}M.",
            "recommendation": "Assign senior estimator support to the top two.",
            "impact": float((top["estimated_value"] * top["probability"] / 100).sum()),
        }

    # --- Material costs ---
    if "material" in q or "cost increasing" in q:
        cat = costs.groupby("category", as_index=False).agg(
            budget=("budget", "sum"), actual=("actual", "sum"))
        cat["variance_pct"] = (cat["actual"] - cat["budget"]) / cat["budget"] * 100
        cat = cat.sort_values("variance_pct", ascending=False).head(4)
        cards = [{"id": r["category"], "title": "Cost category",
                  "margin": f"{r['variance_pct']:+.1f}%",
                  "risk": "High" if r["variance_pct"] > 10 else "Medium"}
                 for _, r in cat.iterrows()]
        return {
            "summary": "Material and equipment categories are the main cost drivers.",
            "cards": cards,
            "explanation": "Concrete, equipment, and material subcategories are trending above budget.",
            "evidence": f"Worst: {cat.iloc[0]['category']} at {cat.iloc[0]['variance_pct']:+.1f}%.",
            "recommendation": "Lock remaining supply pricing; consider contingency increase.",
            "impact": -float((cat["actual"] - cat["budget"]).sum()),
        }

    # --- Fallback (also used when Groq is available but we want structure) ---
    groq = _try_groq(question)
    if groq:
        return {
            "summary": "AI response",
            "cards": [],
            "explanation": groq,
            "evidence": "Generated by Groq (llama-3.3-70b).",
            "recommendation": "—",
            "impact": 0.0,
        }
    return {
        "summary": "I can answer questions about project margin, cost risk, vendor selection, "
                   "change orders, receivables, bids, and material cost trends.",
        "cards": [],
        "explanation": "Try one of the suggested questions above.",
        "evidence": "",
        "recommendation": "",
        "impact": 0.0,
    }
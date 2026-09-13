"""Pure analytics — no UI, no randomness."""
from __future__ import annotations
import pandas as pd
import numpy as np


def executive_kpis(projects: pd.DataFrame,
                   bids: pd.DataFrame,
                   cos: pd.DataFrame,
                   txns: pd.DataFrame) -> dict:
    active = projects[projects["progress"] < 100]
    backlog = float(active["contract_value"].sum())

    open_pipeline = bids[bids["status"].isin(
        ["Research", "Estimating", "Internal Review", "Submitted", "Negotiation"]
    )]
    pipeline = float((open_pipeline["estimated_value"] * open_pipeline["probability"] / 100).sum())

    projected_profit = float((projects["contract_value"] - projects["forecast_cost"]).sum())

    at_risk_projects = projects[projects["risk_level"].isin(["High", "Critical"])]
    at_risk_value = float((at_risk_projects["contract_value"] - at_risk_projects["forecast_cost"]).sum())

    outstanding = float(txns[(txns["type"] == "Receivable") &
                             (txns["status"].isin(["Pending", "Overdue"]))]["amount"].sum())

    return {
        "active_projects": int(len(active)),
        "backlog": backlog,
        "pipeline": pipeline,
        "projected_profit": projected_profit,
        "at_risk_value": at_risk_value,
        "outstanding": outstanding,
    }


def profitability_frame(projects: pd.DataFrame) -> pd.DataFrame:
    df = projects.copy()
    df["Projected Profit"] = df["contract_value"] - df["forecast_cost"]
    df["Margin %"] = df["Projected Profit"] / df["contract_value"] * 100
    return df


def scan_risks(projects: pd.DataFrame,
               cos: pd.DataFrame,
               txns: pd.DataFrame) -> list[dict]:
    risks = []

    eroded = projects[projects["margin_erosion"] >= 3.0].sort_values("margin_erosion", ascending=False)
    for _, r in eroded.iterrows():
        impact = -(r["margin_erosion"] / 100) * r["contract_value"]
        risks.append({
            "severity": "Critical" if r["margin_erosion"] >= 4 else "High",
            "category": "Margin erosion",
            "project_id": r["project_id"],
            "project_name": r["project_name"],
            "detail": (f"Projected margin dropped from {r['original_margin']:.1f}% "
                       f"to {r['expected_margin']:.1f}%"),
            "impact": impact,
            "cause": "Material, equipment, and labor cost pressure",
        })

    overdue = txns[(txns["type"] == "Receivable") & (txns["status"] == "Overdue")]
    for _, r in overdue.iterrows():
        risks.append({
            "severity": "High",
            "category": "Outstanding payment",
            "project_id": r["project_id"],
            "project_name": "—",
            "detail": f"{r['reference']} · 29 days overdue",
            "impact": -float(r["amount"]),
            "cause": "Owner payment delay",
        })

    aged = cos[(cos["days_pending"] >= 10) & (cos["status"].isin(
        ["Pending Approval", "Under Review", "Submitted"]))]
    for _, r in aged.iterrows():
        risks.append({
            "severity": "Medium",
            "category": "Aging change order",
            "project_id": r["project_id"],
            "project_name": "—",
            "detail": f"{r['co_id']} pending {int(r['days_pending'])} days",
            "impact": -float(r["requested_amount"]) * 0.15,
            "cause": "Owner review bottleneck",
        })

    return risks


def portfolio_risk_score(risks: list[dict]) -> tuple[int, str]:
    if not risks:
        return 0, "Healthy"
    weighted = 0
    for r in risks:
        w = {"Critical": 30, "High": 18, "Medium": 8, "Low": 3}.get(r["severity"], 5)
        weighted += w
    score = int(min(100, weighted))
    label = ("Critical" if score >= 80 else
             "High" if score >= 60 else
             "Moderate" if score >= 35 else
             "Low")
    return score, label


def cost_by_category(costs: pd.DataFrame, project_id: str) -> pd.DataFrame:
    df = costs[costs["project_id"] == project_id].copy()
    if df.empty:
        return df
    grouped = df.groupby("category", as_index=False).agg(
        budget=("budget", "sum"),
        actual=("actual", "sum"),
        forecast=("forecast", "sum"),
    )
    grouped["variance"] = grouped["actual"] - grouped["budget"]
    grouped["variance_pct"] = grouped["variance"] / grouped["budget"] * 100
    return grouped.sort_values("variance_pct", ascending=False)


def score_quote(row: pd.Series, min_price: float) -> float:
    price_score = 100 - (row["price"] - min_price) / min_price * 100
    coverage_score = row["scope_coverage"]
    schedule_score = max(0, 100 - (row["timeline_weeks"] - 12) * 5)
    warranty_score = min(100, row["warranty_years"] * 33)
    exp_score = {"Excellent": 100, "Good": 80, "Fair": 60}.get(row["experience"], 70)
    terms_score = 100 if row["payment_terms"] == "Net 30" else 80 if "Net" in str(row["payment_terms"]) else 60

    return round(
        price_score * 0.25 +
        coverage_score * 0.25 +
        schedule_score * 0.20 +
        warranty_score * 0.15 +
        exp_score * 0.10 +
        terms_score * 0.05,
        1,
    )


def financial_summary(projects: pd.DataFrame, txns: pd.DataFrame) -> dict:
    revenue = float(projects["contract_value"].sum())
    actual = float(projects["actual_cost"].sum())
    forecast = float(projects["forecast_cost"].sum())
    profit = revenue - forecast
    collected = float(txns[(txns["type"] == "Receivable") &
                           (txns["status"] == "Paid")]["amount"].sum())
    outstanding = float(txns[(txns["type"] == "Receivable") &
                             (txns["status"].isin(["Pending", "Overdue"]))]["amount"].sum())
    return {
        "contract_revenue": revenue,
        "actual_cost": actual,
        "forecast_cost": forecast,
        "projected_profit": profit,
        "collected": collected,
        "outstanding": outstanding,
    }


def monthly_revenue_cost(projects: pd.DataFrame) -> pd.DataFrame:
    months = pd.date_range("2026-01-01", "2026-12-01", freq="MS")
    rows = []
    total_rev = float(projects["contract_value"].sum())
    total_cost = float(projects["actual_cost"].sum())
    weights = np.array([3, 4, 5, 6, 7, 8, 8, 9, 8, 7, 6, 5], dtype=float)
    weights = weights / weights.sum()
    for i, m in enumerate(months):
        rows.append({
            "month": m,
            "revenue": total_rev * weights[i],
            "cost": total_cost * weights[i],
        })
    df = pd.DataFrame(rows)
    df["profit"] = df["revenue"] - df["cost"]
    return df
"""Data loading. All datasets are generated deterministically so the demo
works offline with realistic, internally consistent construction data."""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
def _projects_df() -> pd.DataFrame:
    rows = [
        ("WW-24015", "South County Water Treatment Improvements", "South County Water District", "Eugene, OR",
         4_820_000, 4_120_000, 2_540_000, 3_940_000, 14.5, 18.2, 78, "Healthy", "Low", "M. Alvarez", "2025-03-04"),
        ("WW-24018", "Eastside Wastewater Treatment Expansion", "City Water Authority", "Portland, OR",
         8_450_000, 7_120_000, 5_080_000, 7_320_000, 17.4, 13.4, 64, "At Risk", "Critical", "J. Whitaker", "2025-01-20"),
        ("WW-24011", "Riverside Water Main Replacement", "Riverside Municipal Utility", "Salem, OR",
         5_640_000, 4_810_000, 3_920_000, 5_020_000, 14.7, 10.8, 82, "At Risk", "High", "K. O'Brien", "2024-11-12"),
        ("WW-24021", "North Valley Pump Station", "North Valley Water Authority", "Vancouver, WA",
         3_260_000, 2_810_000, 1_640_000, 2_920_000, 15.8, 15.2, 55, "Watch", "Medium", "D. Chen", "2025-04-02"),
        ("WW-24008", "Municipal Lift Station Upgrade", "City of Bend Public Works", "Bend, OR",
         2_180_000, 1_860_000, 1_420_000, 1_910_000, 16.1, 12.4, 88, "Watch", "High", "S. Patel", "2024-08-15"),
        ("WW-24024", "Harborview Treatment Plant Phase 2", "Harborview Sanitation District", "Astoria, OR",
         12_400_000, 10_450_000, 6_820_000, 10_180_000, 15.6, 17.9, 61, "Healthy", "Low", "R. Nguyen", "2025-02-18"),
        ("WW-24005", "Willamette Pump Station Modernization", "Willamette Valley Water", "Corvallis, OR",
         6_920_000, 5_890_000, 4_640_000, 6_120_000, 15.1, 11.6, 91, "At Risk", "High", "T. Brooks", "2024-06-10"),
        ("WW-24027", "Cedar Creek Wastewater Interceptor", "Cedar Creek Utility District", "Gresham, OR",
         4_280_000, 3_640_000, 2_180_000, 3_510_000, 15.0, 18.0, 58, "Healthy", "Low", "A. Kowalski", "2025-03-22"),
        ("WW-24030", "Lakeview Water Reclamation Facility", "Lakeview Water Reclamation", "Medford, OR",
         9_840_000, 8_320_000, 4_120_000, 8_020_000, 15.4, 18.5, 46, "Healthy", "Low", "P. Hernandez", "2025-05-06"),
        ("WW-24002", "Downtown Water Main Rehabilitation", "City of Portland Water Bureau", "Portland, OR",
         3_740_000, 3_180_000, 2_980_000, 3_280_000, 15.0, 12.3, 96, "Watch", "Medium", "M. Alvarez", "2024-03-01"),
        ("WW-24033", "Mill Creek Pump Station Expansion", "Mill Creek Water District", "Hillsboro, OR",
         5_120_000, 4_340_000, 2_240_000, 4_210_000, 15.2, 17.8, 51, "Healthy", "Low", "D. Chen", "2025-05-20"),
        ("WW-24036", "Westside Treatment Upgrade", "Westside Water Authority", "Beaverton, OR",
         7_650_000, 6_490_000, 3_180_000, 6_260_000, 15.2, 18.2, 44, "Healthy", "Low", "K. O'Brien", "2025-06-02"),
        ("WW-24019", "Highland Reservoir Rehabilitation", "Highland Water District", "Tigard, OR",
         2_940_000, 2_490_000, 1_860_000, 2_420_000, 15.3, 17.7, 71, "Healthy", "Low", "S. Patel", "2025-02-10"),
        ("WW-24014", "Sunrise Lift Station Replacement", "Sunrise Utility District", "Lake Oswego, OR",
         1_840_000, 1_560_000, 1_280_000, 1_640_000, 15.2, 10.9, 84, "At Risk", "High", "T. Brooks", "2024-10-05"),
        ("WW-24042", "Greenfield Water Treatment Plant", "Greenfield Water Commission", "Wilsonville, OR",
         14_200_000, 12_040_000, 4_180_000, 11_680_000, 15.2, 17.7, 34, "Healthy", "Low", "R. Nguyen", "2025-07-15"),
    ]
    cols = ["project_id", "project_name", "owner", "location", "contract_value",
            "budget", "actual_cost", "forecast_cost", "original_margin",
            "expected_margin", "progress", "status", "risk_level", "pm", "start_date"]
    df = pd.DataFrame(rows, columns=cols)
    df["projected_profit"] = df["contract_value"] - df["forecast_cost"]
    df["cost_variance"] = df["actual_cost"] - (df["budget"] * df["progress"] / 100)
    df["margin_erosion"] = df["original_margin"] - df["expected_margin"]
    df["start_date"] = pd.to_datetime(df["start_date"])
    return df


# ---------------------------------------------------------------------------
# Bids
# ---------------------------------------------------------------------------
def _bids_df() -> pd.DataFrame:
    rows = [
        ("BID-3001", "Eastside Wastewater Treatment Expansion", "City Water Authority", "Portland, OR",
         "Wastewater Treatment", 8_450_000, "2026-09-28", 72, "J. Whitaker", "Estimating"),
        ("BID-3002", "North Valley Pump Station", "North Valley Water Authority", "Vancouver, WA",
         "Pump Station", 3_260_000, "2026-10-14", 68, "D. Chen", "Submitted"),
        ("BID-3003", "Riverside Water Main Replacement", "Riverside Municipal Utility", "Salem, OR",
         "Water Main", 5_640_000, "2026-11-02", 55, "K. O'Brien", "Internal Review"),
        ("BID-3004", "Municipal Lift Station Upgrade", "City of Bend Public Works", "Bend, OR",
         "Lift Station", 2_180_000, "2026-09-22", 81, "S. Patel", "Negotiation"),
        ("BID-3005", "South County Water Treatment Improvements", "South County Water District", "Eugene, OR",
         "Treatment Plant", 4_820_000, "2026-12-05", 44, "M. Alvarez", "Estimating"),
        ("BID-3006", "Harborview Treatment Plant Phase 2", "Harborview Sanitation District", "Astoria, OR",
         "Treatment Plant", 12_400_000, "2026-10-30", 62, "R. Nguyen", "Submitted"),
        ("BID-3007", "Willamette Pump Station Modernization", "Willamette Valley Water", "Corvallis, OR",
         "Pump Station", 6_920_000, "2026-11-18", 58, "T. Brooks", "Internal Review"),
        ("BID-3008", "Cedar Creek Wastewater Interceptor", "Cedar Creek Utility District", "Gresham, OR",
         "Wastewater", 4_280_000, "2026-10-08", 70, "A. Kowalski", "Estimating"),
        ("BID-3009", "Lakeview Water Reclamation Facility", "Lakeview Water Reclamation", "Medford, OR",
         "Treatment Plant", 9_840_000, "2026-11-25", 48, "P. Hernandez", "Research"),
        ("BID-3010", "Downtown Water Main Rehabilitation", "City of Portland Water Bureau", "Portland, OR",
         "Water Main", 3_740_000, "2026-09-15", 76, "M. Alvarez", "Negotiation"),
        ("BID-3011", "Mill Creek Pump Station Expansion", "Mill Creek Water District", "Hillsboro, OR",
         "Pump Station", 5_120_000, "2026-12-12", 42, "D. Chen", "Estimating"),
        ("BID-3012", "Westside Treatment Upgrade", "Westside Water Authority", "Beaverton, OR",
         "Treatment Plant", 7_650_000, "2026-10-20", 65, "K. O'Brien", "Submitted"),
        ("BID-3013", "Highland Reservoir Rehabilitation", "Highland Water District", "Tigard, OR",
         "Reservoir", 2_940_000, "2026-11-08", 71, "S. Patel", "Internal Review"),
        ("BID-3014", "Sunrise Lift Station Replacement", "Sunrise Utility District", "Lake Oswego, OR",
         "Lift Station", 1_840_000, "2026-09-19", 79, "T. Brooks", "Negotiation"),
        ("BID-3015", "Greenfield Water Treatment Plant", "Greenfield Water Commission", "Wilsonville, OR",
         "Treatment Plant", 14_200_000, "2026-12-20", 38, "R. Nguyen", "Research"),
        ("BID-3016", "Rivergate Wastewater Pump Station", "Rivergate Sanitation", "Oregon City, OR",
         "Pump Station", 4_560_000, "2026-10-28", 60, "A. Kowalski", "Estimating"),
        ("BID-3017", "Blue Ridge Water Storage Tank", "Blue Ridge Water District", "Newberg, OR",
         "Storage Tank", 2_280_000, "2026-11-14", 66, "P. Hernandez", "Submitted"),
        ("BID-3018", "Silver Creek Treatment Plant Upgrade", "Silver Creek Utility Authority", "McMinnville, OR",
         "Treatment Plant", 6_340_000, "2026-12-02", 47, "M. Alvarez", "Estimating"),
        ("BID-3019", "Cascade Water Main Extension", "Cascade Water District", "Troutdale, OR",
         "Water Main", 3_120_000, "2026-10-10", 73, "D. Chen", "Internal Review"),
        ("BID-3020", "Meadowbrook Pump Station Rehab", "Meadowbrook Water District", "Tualatin, OR",
         "Pump Station", 2_680_000, "2026-11-20", 62, "K. O'Brien", "Submitted"),
        ("BID-3021", "Fairview Wastewater Treatment Expansion", "Fairview Sanitation District", "Fairview, OR",
         "Wastewater Treatment", 7_180_000, "2026-12-15", 41, "S. Patel", "Research"),
        ("BID-3022", "Oak Ridge Water Reclamation Project", "Oak Ridge Water Authority", "Sherwood, OR",
         "Water Reclamation", 5_780_000, "2026-10-24", 64, "T. Brooks", "Estimating"),
        ("BID-3023", "Pine Valley Water Main Replacement", "Pine Valley Water District", "Forest Grove, OR",
         "Water Main", 3_460_000, "2026-11-06", 68, "R. Nguyen", "Submitted"),
        ("BID-3024", "Riverbend Lift Station Upgrade", "Riverbend Utility District", "Canby, OR",
         "Lift Station", 2_020_000, "2026-09-26", 77, "A. Kowalski", "Negotiation"),
        ("BID-3025", "Summit Water Treatment Facility", "Summit Water Commission", "West Linn, OR",
         "Treatment Plant", 10_240_000, "2026-12-09", 45, "P. Hernandez", "Estimating"),
        ("BID-3026", "Lakeshore Wastewater Collection", "Lakeshore Sanitation District", "Lake Grove, OR",
         "Wastewater", 4_880_000, "2026-10-17", 59, "M. Alvarez", "Submitted"),
        ("BID-3027", "Chestnut Creek Pump Station", "Chestnut Creek Water District", "Gladstone, OR",
         "Pump Station", 3_640_000, "2026-11-12", 67, "D. Chen", "Internal Review"),
        ("BID-3028", "Willow Creek Reservoir Expansion", "Willow Creek Water Authority", "Milwaukie, OR",
         "Reservoir", 4_140_000, "2026-12-18", 40, "K. O'Brien", "Research"),
        ("BID-3029", "Stonebridge Water Main Project", "Stonebridge Water District", "Happy Valley, OR",
         "Water Main", 2_520_000, "2026-10-22", 71, "S. Patel", "Estimating"),
        ("BID-3030", "Hillside Water Reclamation Upgrade", "Hillside Water Commission", "Damascus, OR",
         "Water Reclamation", 6_780_000, "2026-11-28", 53, "T. Brooks", "Submitted"),
    ]
    cols = ["opportunity_id", "project", "owner", "location", "project_type",
            "estimated_value", "bid_due", "probability", "estimator", "status"]
    df = pd.DataFrame(rows, columns=cols)
    df["bid_due"] = pd.to_datetime(df["bid_due"])
    return df


# ---------------------------------------------------------------------------
# Cost detail (100+ records)
# ---------------------------------------------------------------------------
_COST_CATEGORIES = [
    ("Concrete", "Structural foundation", 2400, "CY", 185),
    ("Concrete", "Reinforced walls", 1800, "CY", 210),
    ("Concrete", "Slabs and footings", 950, "CY", 165),
    ("Concrete", "Formwork", 12500, "SF", 28),
    ("Piping", "Process piping", 8500, "LF", 74),
    ("Piping", "Underground utilities", 4200, "LF", 96),
    ("Piping", "HDPE force main", 3100, "LF", 118),
    ("Piping", "Ductile iron pipe", 2800, "LF", 88),
    ("Mechanical", "Pumps & motors", 6, "EA", 145000),
    ("Mechanical", "Valves & actuators", 42, "EA", 8200),
    ("Mechanical", "HVAC systems", 1, "LS", 320000),
    ("Mechanical", "Blowers", 4, "EA", 62000),
    ("Electrical", "MCC panels", 8, "EA", 48000),
    ("Electrical", "Wiring & conduit", 24000, "LF", 22),
    ("Electrical", "Instrumentation", 1, "LS", 185000),
    ("Electrical", "SCADA integration", 1, "LS", 142000),
    ("Equipment", "Excavators", 1200, "HR", 165),
    ("Equipment", "Cranes", 640, "HR", 285),
    ("Equipment", "Concrete pumps", 380, "HR", 195),
    ("Equipment", "Dewatering", 1, "LS", 96000),
    ("Labor", "Concrete crew", 6400, "HR", 52),
    ("Labor", "Pipefitters", 8200, "HR", 68),
    ("Labor", "Electricians", 4800, "HR", 72),
    ("Labor", "Ironworkers", 3600, "HR", 64),
    ("Labor", "Operating engineers", 4200, "HR", 58),
    ("Labor", "General laborers", 12500, "HR", 48),
    ("Subcontractors", "Site clearing", 1, "LS", 145000),
    ("Subcontractors", "Painting & coatings", 1, "LS", 88000),
    ("Subcontractors", "Roofing", 1, "LS", 124000),
    ("Subcontractors", "Landscaping", 1, "LS", 56000),
    ("Other", "Permits & fees", 1, "LS", 68000),
    ("Other", "Engineering support", 1, "LS", 185000),
    ("Other", "Temporary facilities", 1, "LS", 74000),
    ("Other", "Safety & PPE", 1, "LS", 42000),
]


def _costs_df() -> pd.DataFrame:
    projects = _projects_df()
    rows = []
    rng = np.random.default_rng(42)
    for _, p in projects.iterrows():
        n = 7
        sample = rng.choice(len(_COST_CATEGORIES), size=n, replace=False)
        for idx in sample:
            cat, desc, qty, unit, unit_cost = _COST_CATEGORIES[int(idx)]
            factor = max(0.6, min(1.6, p["contract_value"] / 5_000_000))
            q = round(qty * factor, 0)
            base_total = q * unit_cost
            variance = float(rng.normal(0, 0.08))
            actual = base_total * (1 + variance)
            forecast = base_total * (1 + variance * 0.9)
            rows.append({
                "project_id": p["project_id"],
                "category": cat,
                "description": desc,
                "quantity": q,
                "unit": unit,
                "unit_cost": unit_cost,
                "budget": round(base_total, 2),
                "actual": round(actual, 2),
                "forecast": round(forecast, 2),
            })
    df = pd.DataFrame(rows)
    mask = (df["project_id"] == "WW-24018") & (df["category"].isin(["Concrete", "Equipment", "Labor"]))
    df.loc[mask, "actual"] *= 1.14
    df.loc[mask, "forecast"] *= 1.13
    df["variance"] = df["actual"] - df["budget"]
    df["variance_pct"] = df["variance"] / df["budget"] * 100
    df["total"] = df["unit_cost"] * df["quantity"]
    return df


# ---------------------------------------------------------------------------
# Vendors / Quotes
# ---------------------------------------------------------------------------
def _vendors_df() -> pd.DataFrame:
    rows = [
        ("V-001", "Apex Mechanical", "Mechanical", "Sarah Connor", "sconnor@apexmec.com", "503-555-0110", 4.7, 18, "Portland", "OR"),
        ("V-002", "Northwest Process", "Mechanical", "Bill Hartman", "bhartman@nwprocess.com", "503-555-0121", 4.2, 12, "Salem", "OR"),
        ("V-003", "Cascade Industrial", "Mechanical", "Elena Vasquez", "evasquez@cascade-ind.com", "503-555-0132", 4.9, 22, "Portland", "OR"),
        ("V-004", "Pacific Concrete Co.", "Concrete", "Tom Reyes", "treyes@pacconcrete.com", "503-555-0143", 4.6, 25, "Vancouver", "WA"),
        ("V-005", "Iron Ridge Structures", "Concrete", "Marta Lindqvist", "ml@ironridge.com", "503-555-0154", 4.4, 15, "Beaverton", "OR"),
        ("V-006", "Willamette Piping", "Piping", "David Park", "dpark@wpiping.com", "503-555-0165", 4.8, 20, "Eugene", "OR"),
        ("V-007", "Columbia Pipe & Supply", "Piping", "Jennifer Yu", "jyu@columbiapipe.com", "503-555-0176", 4.5, 17, "Portland", "OR"),
        ("V-008", "Volt Electric", "Electrical", "Raj Patel", "rpatel@voltelectric.com", "503-555-0187", 4.6, 19, "Portland", "OR"),
        ("V-009", "Summit Electrical", "Electrical", "Greg Moore", "gmoore@summitelec.com", "503-555-0198", 4.3, 14, "Tigard", "OR"),
        ("V-010", "Basin Equipment Rental", "Equipment", "Linda Tan", "ltan@basinequip.com", "503-555-0209", 4.5, 16, "Portland", "OR"),
        ("V-011", "West Coast Excavation", "Civil", "Marcus Webb", "mwebb@wcexc.com", "503-555-0210", 4.7, 21, "Gresham", "OR"),
        ("V-012", "Emerald Site Services", "Civil", "Chloe Nguyen", "cnguyen@emeraldsite.com", "503-555-0221", 4.4, 13, "Salem", "OR"),
        ("V-013", "Cascade Coatings", "Painting", "Ron Halvorsen", "rhalvorsen@cascadecoat.com", "503-555-0232", 4.6, 18, "Hillsboro", "OR"),
        ("V-014", "Northwest Roofing Group", "Roofing", "Tina Alvarado", "talvarado@nwroofing.com", "503-555-0243", 4.5, 15, "Portland", "OR"),
        ("V-015", "Pacific Instrumentation", "Instrumentation", "Steve Kowalski", "skowalski@pacinstr.com", "503-555-0254", 4.8, 20, "Beaverton", "OR"),
        ("V-016", "Streamline Controls", "Instrumentation", "Amy Chen", "achen@streamlinecontrols.com", "503-555-0265", 4.4, 12, "Portland", "OR"),
        ("V-017", "Valley HVAC Solutions", "HVAC", "Brian Foster", "bfoster@valleyhvac.com", "503-555-0276", 4.6, 17, "Salem", "OR"),
        ("V-018", "Apex Pump Systems", "Equipment", "Dana Ruiz", "druiz@apexpumps.com", "503-555-0287", 4.7, 19, "Portland", "OR"),
        ("V-019", "Trident Marine Contracting", "Marine", "Karl Johansson", "kjohansson@tridentmarine.com", "503-555-0298", 4.5, 22, "Astoria", "OR"),
        ("V-020", "Greenway Landscaping", "Landscaping", "Olivia Bennett", "obennett@greenwayland.com", "503-555-0309", 4.3, 11, "Lake Oswego", "OR"),
    ]
    cols = ["vendor_id", "vendor_name", "trade", "contact", "email", "phone",
            "rating", "years_in_business", "city", "state"]
    return pd.DataFrame(rows, columns=cols)


def _quotes_df() -> pd.DataFrame:
    rows = [
        ("Q-5001", "WW-24018", "V-001", "Mechanical", 1_240_000, 96, 18, 2, "Net 30", "Excellent", 91),
        ("Q-5002", "WW-24018", "V-002", "Mechanical", 1_180_000, 87, 22, 1, "40% advance", "Good", 78),
        ("Q-5003", "WW-24018", "V-003", "Mechanical", 1_295_000, 100, 16, 3, "Net 30", "Excellent", 95),
        ("Q-5004", "WW-24018", "V-018", "Equipment", 620_000, 94, 20, 2, "Net 45", "Excellent", 88),
        ("Q-5005", "WW-24018", "V-015", "Instrumentation", 185_000, 100, 14, 3, "Net 30", "Excellent", 93),
    ]
    cols = ["quote_id", "project_id", "vendor_id", "scope", "price", "scope_coverage",
            "timeline_weeks", "warranty_years", "payment_terms", "experience", "ai_score"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------------------
# Change Orders
# ---------------------------------------------------------------------------
def _change_orders_df() -> pd.DataFrame:
    rows = [
        ("CO-1048", "WW-24018", "Additional underground piping", 284_000, 192_000, "Pending Approval", 12, "J. Whitaker", "2026-08-15"),
        ("CO-1049", "WW-24018", "Additional concrete foundation work", 142_000, 98_000, "Under Review", 7, "J. Whitaker", "2026-08-20"),
        ("CO-1050", "WW-24011", "Rock excavation allowance", 168_000, 122_000, "Approved", 0, "K. O'Brien", "2026-07-28"),
        ("CO-1051", "WW-24011", "Relocated valve vault", 84_000, 58_000, "Submitted", 5, "K. O'Brien", "2026-08-22"),
        ("CO-1052", "WW-24021", "Extended dewatering operation", 62_000, 44_000, "Pending Approval", 3, "D. Chen", "2026-08-24"),
        ("CO-1053", "WW-24008", "Additional instrumentation", 118_000, 82_000, "Approved", 0, "S. Patel", "2026-07-15"),
        ("CO-1054", "WW-24024", "Site access modifications", 96_000, 68_000, "Under Review", 9, "R. Nguyen", "2026-08-18"),
        ("CO-1055", "WW-24005", "Pipe rerouting around existing utilities", 224_000, 158_000, "Pending Approval", 15, "T. Brooks", "2026-08-12"),
        ("CO-1056", "WW-24005", "Additional shoring requirements", 138_000, 104_000, "Submitted", 6, "T. Brooks", "2026-08-21"),
        ("CO-1057", "WW-24027", "Expanded site grading", 74_000, 52_000, "Approved", 0, "A. Kowalski", "2026-07-30"),
        ("CO-1058", "WW-24014", "Replacement pump upgrade", 92_000, 66_000, "Rejected", 0, "T. Brooks", "2026-06-20"),
        ("CO-1059", "WW-24019", "Reservoir liner upgrade", 68_000, 48_000, "Approved", 0, "S. Patel", "2026-08-05"),
        ("CO-1060", "WW-24030", "Additional treatment process equipment", 312_000, 218_000, "Submitted", 4, "P. Hernandez", "2026-08-23"),
        ("CO-1061", "WW-24002", "Traffic control extension", 42_000, 30_000, "Approved", 0, "M. Alvarez", "2026-07-22"),
        ("CO-1062", "WW-24033", "Geotechnical allowance increase", 128_000, 92_000, "Under Review", 8, "D. Chen", "2026-08-19"),
    ]
    cols = ["co_id", "project_id", "description", "requested_amount", "cost",
            "status", "days_pending", "owner", "submitted_date"]
    df = pd.DataFrame(rows, columns=cols)
    df["potential_profit"] = df["requested_amount"] - df["cost"]
    df["margin_pct"] = df["potential_profit"] / df["requested_amount"] * 100
    return df


# ---------------------------------------------------------------------------
# Financial transactions (100+)
# ---------------------------------------------------------------------------
def _transactions_df() -> pd.DataFrame:
    projects = _projects_df()
    rng = np.random.default_rng(7)
    rows = []
    apps = ["#APP-", "#INV-", "#PAY-"]
    for _, p in projects.iterrows():
        n = 8
        for i in range(n):
            month = int(rng.integers(1, 9))
            day = int(rng.integers(1, 28))
            direction = "Receivable" if i % 2 == 0 else "Payable"
            amount = float(rng.uniform(0.05, 0.35) * p["contract_value"] / 6)
            status = "Paid" if i < 5 else ("Pending" if i < 7 else "Overdue")
            rows.append({
                "txn_id": f"TXN-{1000 + len(rows)}",
                "project_id": p["project_id"],
                "type": direction,
                "reference": f"{apps[i % 3]}{1000 + len(rows)}",
                "amount": round(amount, 2),
                "status": status,
                "date": f"2026-{month:02d}-{day:02d}",
            })
    df = pd.DataFrame(rows)
    idx = (df["project_id"] == "WW-24011") & (df["status"] == "Pending")
    if idx.any():
        first = df[idx].index[0]
        df.at[first, "amount"] = 420_000
        df.at[first, "status"] = "Overdue"
        df.at[first, "type"] = "Receivable"
    df["date"] = pd.to_datetime(df["date"])
    return df


# ---------------------------------------------------------------------------
# Public loaders (cached)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_projects() -> pd.DataFrame:
    return _projects_df()


@st.cache_data(show_spinner=False)
def load_bids() -> pd.DataFrame:
    return _bids_df()


@st.cache_data(show_spinner=False)
def load_costs() -> pd.DataFrame:
    return _costs_df()


@st.cache_data(show_spinner=False)
def load_vendors() -> pd.DataFrame:
    return _vendors_df()


@st.cache_data(show_spinner=False)
def load_quotes() -> pd.DataFrame:
    return _quotes_df()


@st.cache_data(show_spinner=False)
def load_change_orders() -> pd.DataFrame:
    return _change_orders_df()


@st.cache_data(show_spinner=False)
def load_transactions() -> pd.DataFrame:
    return _transactions_df()


# ---------------------------------------------------------------------------
# CSV persistence helper (optional)
# ---------------------------------------------------------------------------
def _write_csvs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    load_projects().to_csv(os.path.join(DATA_DIR, "projects.csv"), index=False)
    load_bids().to_csv(os.path.join(DATA_DIR, "bids.csv"), index=False)
    load_costs().to_csv(os.path.join(DATA_DIR, "costs.csv"), index=False)
    load_vendors().to_csv(os.path.join(DATA_DIR, "vendors.csv"), index=False)
    load_quotes().to_csv(os.path.join(DATA_DIR, "quotes.csv"), index=False)
    load_change_orders().to_csv(os.path.join(DATA_DIR, "change_orders.csv"), index=False)
    load_transactions().to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)


if __name__ == "__main__":
    _write_csvs()
    print(f"Demo data written to {DATA_DIR}")
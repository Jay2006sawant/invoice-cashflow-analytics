"""
Generate a realistic synthetic invoice dataset for working-capital analytics.

Simulates invoice payment behavior across SMB, Mid-Market, and Enterprise segments
with seasonality, chronic late payers, and a mix of paid/late/outstanding invoices.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Analysis "as of" date — unpaid invoices remain open through this date.
AS_OF_DATE = date(2026, 5, 10)
MONTHS_BACK = 18
TARGET_ROWS = 2500
RANDOM_SEED = 42

CUSTOMERS = [
    ("Acme Logistics", "SMB", 0.15),
    ("Brightline Retail", "SMB", 0.35),
    ("Cascade Foods", "Mid-Market", 0.10),
    ("Delta Manufacturing", "Enterprise", 0.25),
    ("Evergreen Health", "Mid-Market", 0.05),
    ("Frontier Tech", "SMB", 0.20),
    ("Granite Construction", "Enterprise", 0.30),
    ("Horizon Media", "Mid-Market", 0.12),
    ("Ironclad Security", "SMB", 0.40),
    ("Juniper Consulting", "Mid-Market", 0.08),
    ("Keystone Energy", "Enterprise", 0.18),
    ("Lumen Software", "SMB", 0.22),
    ("Meridian Pharma", "Enterprise", 0.15),
    ("Northstar Wholesale", "Mid-Market", 0.28),
    ("Orion Aerospace", "Enterprise", 0.20),
    ("Pinnacle Insurance", "Mid-Market", 0.14),
    ("Quantum Analytics", "SMB", 0.18),
    ("Riverstone Hotels", "Mid-Market", 0.32),
    ("Summit Financial", "Enterprise", 0.12),
    ("Terra Farms", "SMB", 0.25),
    ("Union Transport", "Mid-Market", 0.38),
    ("Vertex Biotech", "Enterprise", 0.10),
    ("Westfield Properties", "Mid-Market", 0.16),
    ("Xeno Packaging", "SMB", 0.30),
    ("Yellowstone Mining", "Enterprise", 0.22),
]

VENDORS = [
    "CloudServe Inc",
    "DataPipe Solutions",
    "FleetManage Co",
    "GreenLedger Systems",
    "InsightOps Ltd",
    "NetScale Partners",
    "PayFlow Technologies",
    "SupplyChain Pro",
    "TradeLedger Finance",
    "WorkCapital Hub",
]

SEGMENT_TERMS = {"SMB": 30, "Mid-Market": 45, "Enterprise": 60}
SEGMENT_AMOUNT = {
    "SMB": (800, 12000),
    "Mid-Market": (5000, 45000),
    "Enterprise": (25000, 180000),
}


def month_seasonality(month: int) -> float:
    """Higher invoice volume in Q4; slower collections in summer."""
    seasonal = {1: 0.95, 2: 0.90, 3: 1.00, 4: 1.05, 5: 1.00, 6: 0.92,
                7: 0.88, 8: 0.90, 9: 1.05, 10: 1.10, 11: 1.15, 12: 1.20}
    return seasonal[month]


def generate_invoice_id(index: int) -> str:
    return f"INV-{AS_OF_DATE.year}-{index:05d}"


def sample_invoice_date(rng: np.random.Generator) -> date:
    start = AS_OF_DATE - timedelta(days=MONTHS_BACK * 30)
    days_range = (AS_OF_DATE - start).days
    offset = int(rng.integers(0, days_range))
    candidate = start + timedelta(days=offset)
    weight = month_seasonality(candidate.month)
    if rng.random() > weight / 1.2:
        return sample_invoice_date(rng)
    return candidate


def payment_delay_days(rng: np.random.Generator, segment: str, late_tendency: float) -> int:
    """Delay relative to the due date. Most invoices pay on time or early;
    lateness is driven by each customer's late_tendency probability, with
    larger segments taking somewhat longer to resolve once late."""
    if rng.random() < late_tendency:
        max_delay = {"SMB": 45, "Mid-Market": 65, "Enterprise": 90}[segment]
        return int(rng.integers(1, max_delay))
    return int(rng.integers(-10, 1))


def build_row(index: int, rng: np.random.Generator) -> dict:
    customer_name, segment, late_tendency = CUSTOMERS[rng.integers(0, len(CUSTOMERS))]
    invoice_date = sample_invoice_date(rng)
    payment_terms = SEGMENT_TERMS[segment]
    due_date = invoice_date + timedelta(days=payment_terms)

    low, high = SEGMENT_AMOUNT[segment]
    invoice_amount = round(float(rng.uniform(low, high)), 2)

    # Recent invoices more likely to remain outstanding.
    days_since_invoice = (AS_OF_DATE - invoice_date).days
    outstanding_prob = 0.08 if days_since_invoice > 90 else 0.22 if days_since_invoice > 45 else 0.35

    if rng.random() < outstanding_prob and due_date <= AS_OF_DATE:
        payment_date = None
        payment_status = "Outstanding"
    else:
        delay = payment_delay_days(rng, segment, late_tendency)
        payment_date = due_date + timedelta(days=delay)

        if payment_date > AS_OF_DATE:
            payment_date = None
            payment_status = "Outstanding"
        elif delay > 0:
            payment_status = "Late"
        else:
            payment_status = "Paid"

    return {
        "invoice_id": generate_invoice_id(index),
        "customer_name": customer_name,
        "customer_segment": segment,
        "vendor_name": VENDORS[rng.integers(0, len(VENDORS))],
        "invoice_amount": invoice_amount,
        "invoice_date": invoice_date.isoformat(),
        "due_date": due_date.isoformat(),
        "payment_date": payment_date.isoformat() if payment_date else "",
        "payment_status": payment_status,
    }


def main() -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    random.seed(RANDOM_SEED)

    rows = [build_row(i + 1, rng) for i in range(TARGET_ROWS)]
    df = pd.DataFrame(rows)

    # Inject a handful of anomalies for the cleaning script to flag.
    anomaly_indices = rng.choice(len(df), size=8, replace=False)
    for idx in anomaly_indices[:4]:
        df.at[idx, "due_date"] = (
            pd.to_datetime(df.at[idx, "invoice_date"]) - timedelta(days=5)
        ).date().isoformat()
    for idx in anomaly_indices[4:6]:
        df.at[idx, "invoice_amount"] = -abs(df.at[idx, "invoice_amount"])
    for idx in anomaly_indices[6:]:
        df.at[idx, "payment_date"] = (
            pd.to_datetime(df.at[idx, "invoice_date"]) - timedelta(days=2)
        ).date().isoformat()

    output_path = Path(__file__).resolve().parents[1] / "data" / "invoices_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df):,} invoices -> {output_path}")


if __name__ == "__main__":
    main()

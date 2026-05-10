"""
Clean and validate raw invoice data for SQL loading.

Handles missing payment dates, validates date logic, flags anomalies,
and derives days_to_pay and is_late fields.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

AS_OF_DATE = pd.Timestamp("2026-05-10")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "invoices_raw.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "invoices_cleaned.csv"
ANOMALY_PATH = PROJECT_ROOT / "data" / "anomalies_flagged.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    date_cols = ["invoice_date", "due_date", "payment_date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def validate_and_flag(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    bad_indices: set[int] = set()
    anomalies = []

    def flag(mask: pd.Series, reason: str) -> None:
        if not mask.any():
            return
        flagged = df.loc[mask].copy()
        flagged["anomaly_reason"] = reason
        anomalies.append(flagged)
        bad_indices.update(flagged.index.tolist())

    flag(df["invoice_amount"] <= 0, "non_positive_invoice_amount")
    flag(df["due_date"] < df["invoice_date"], "due_date_before_invoice_date")
    flag(
        df["payment_date"].notna() & (df["payment_date"] < df["invoice_date"]),
        "payment_date_before_invoice_date",
    )
    flag(
        df["payment_status"].eq("Outstanding") & df["payment_date"].notna(),
        "outstanding_with_payment_date",
    )
    flag(
        df["payment_status"].isin(["Paid", "Late"]) & df["payment_date"].isna(),
        "paid_or_late_missing_payment_date",
    )

    anomaly_df = pd.concat(anomalies, ignore_index=True) if anomalies else pd.DataFrame()
    clean_df = df.drop(index=list(bad_indices)).reset_index(drop=True) if bad_indices else df.copy()
    return clean_df, anomaly_df


def derive_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Outstanding invoices have no payment date; use as-of date for aging only.
    df["days_to_pay"] = (
        df["payment_date"].fillna(AS_OF_DATE) - df["invoice_date"]
    ).dt.days

    df["is_late"] = (
        (df["payment_status"] == "Late")
        | (
            (df["payment_status"] == "Outstanding")
            & (AS_OF_DATE > df["due_date"])
        )
        | (
            df["payment_date"].notna()
            & (df["payment_date"] > df["due_date"])
        )
    ).astype(int)

    df["days_overdue"] = (
        df["payment_date"].fillna(AS_OF_DATE) - df["due_date"]
    ).dt.days.clip(lower=0)

    # Normalize payment_date back to nullable for SQL load.
    df["payment_date"] = df["payment_date"].dt.strftime("%Y-%m-%d")
    df.loc[df["payment_date"].isna(), "payment_date"] = None

    df["invoice_date"] = df["invoice_date"].dt.strftime("%Y-%m-%d")
    df["due_date"] = df["due_date"].dt.strftime("%Y-%m-%d")

    return df


def main() -> None:
    raw = load_raw()
    cleaned, anomalies = validate_and_flag(raw)
    cleaned = derive_fields(cleaned)

    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)

    if not anomalies.empty:
        anomalies.to_csv(ANOMALY_PATH, index=False)
        print(f"Flagged {len(anomalies):,} anomalous rows -> {ANOMALY_PATH}")
    else:
        print("No anomalies flagged.")

    print(f"Cleaned {len(cleaned):,} rows -> {CLEAN_PATH}")


if __name__ == "__main__":
    main()

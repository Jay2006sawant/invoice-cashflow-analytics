# Invoice & Cash Flow Analytics Dashboard

A portfolio analytics project simulating working-capital and invoice-financing analysis for a fintech use case. The pipeline generates synthetic invoice data, cleans and validates it, loads it into SQLite, runs reusable SQL analytics, and exports Tableau-ready datasets plus an Excel summary for stakeholders.

## Problem Statement

Invoice-financing and working-capital teams need to answer:

- How fast are customers paying (DSO)?
- Which customers or segments are chronically late?
- Where should collections focus (aging buckets)?
- How is cash inflow trending month over month?

This project demonstrates an end-to-end analytics workflow: **data generation → cleaning → SQL modeling → dashboard-ready exports → business reporting**.

## Project Structure

```
invoice-cashflow-analytics/
├── data/
│   ├── invoices_raw.csv          # Synthetic source data (~2,500 rows)
│   ├── invoices_cleaned.csv      # Validated data for SQL loading
│   └── anomalies_flagged.csv     # Rows failing validation rules
├── database/
│   └── invoices.db               # SQLite database
├── sql/                          # Reusable analytics queries
├── scripts/
│   ├── generate_data.py          # Synthetic dataset generator
│   ├── clean_data.py             # Pandas cleaning & validation
│   ├── setup_database.py         # DB setup and query runner
│   └── export_reports.py         # Tableau CSV + Excel exports
├── exports/                      # Tableau-ready CSVs + Excel report
└── README.md
```

## Setup & Run

```bash
pip install -r requirements.txt

python scripts/generate_data.py
python scripts/clean_data.py
python scripts/setup_database.py
python scripts/export_reports.py
```

**Analysis as-of date:** 2026-05-10

## Approach

1. **Synthetic data** — 2,500 invoices across 18 months with segment-specific payment terms, Q4 seasonality, summer slowdown, and chronic late payers.
2. **Cleaning** — Null payment dates for outstanding invoices, date-logic validation, anomaly flagging, and derived fields (`days_to_pay`, `is_late`, `days_overdue`).
3. **SQL analytics** — DSO overall/by segment/by month, late rates, aging buckets, and cash inflow trends stored as reusable `.sql` files.
4. **Exports** — Aggregated CSVs for Tableau and a formatted Excel workbook for non-technical stakeholders.

## Key Findings (Sample Insights)

Based on the generated dataset (2,492 cleaned invoices, as of 2026-05-10):

- **Enterprise customers pay slowest on average** — 75.0 days vs. 54.5 for SMB (a ~20.5-day gap), driven by longer 60-day payment terms and a higher share of large, multi-approver invoices.
- **SMB has the highest late-payment rate (31.2%)**, ahead of Enterprise (24.3%) and Mid-Market (22.2%) — smaller accounts are less consistent even though their absolute settlement times are shorter.
- **A concentrated set of chronic late payers drives risk**: Ironclad Security (SMB, 47.2% late rate) is the single worst offender; the next four accounts (Union Transport, Xeno Packaging, Brightline Retail, Granite Construction) each run 30–40% late rates and collectively represent over $14M in invoice value.
- **The 90+ day aging bucket holds meaningful exposure** — $5.4M outstanding across all segments (Enterprise $4.0M, Mid-Market $1.0M, SMB $0.4M) — signaling accounts that may need escalation or invoice-financing intervention.
- **Open AR has grown sharply in the most recent months** (from ~$0.4M in Jan 2026 to $5.4M in Apr 2026) simply because recent invoices haven't had time to be paid yet — this is a normal artifact of the as-of date, not a genuine collections breakdown. Use the trailing months' data with this caveat, or exclude the most recent 30–45 days from trend analysis.

> Re-run `export_reports.py` after regenerating data to refresh these metrics in exports.

## Tableau Dashboard Guide

Import CSVs from `/exports` into Tableau Desktop or Tableau Public.

### 1. DSO Trend Line Chart

**Data source:** `dso_by_month.csv`

| Setting | Value |
|---------|-------|
| Columns | `invoice_month` (continuous date) |
| Rows | `avg_days_to_pay` |
| Chart type | Line |

**Business insight:** Track whether working-capital efficiency is improving or deteriorating. Rising DSO may indicate collections gaps, customer stress, or segment mix shift toward Enterprise. Pair with `monthly_sales` as a secondary axis to distinguish volume-driven DSO moves from true payment slowdowns.

### 2. Aging Bucket Stacked Bar Chart

**Data source:** `aging_buckets.csv`

| Setting | Value |
|---------|-------|
| Columns | `aging_bucket` (ordered: Current → 0-30 → 31-60 → 61-90 → 90+) |
| Rows | `outstanding_amount` |
| Color | `customer_segment` |
| Chart type | Stacked bar |

**Business insight:** Shows where collections effort should focus. The 61–90 and 90+ buckets represent escalating credit risk — prioritize outreach, payment plans, or invoice financing for these accounts. Segment color reveals whether Enterprise or SMB drives overdue exposure.

### 3. Top 10 Late-Paying Customers Table

**Data source:** `top_late_payers.csv`

| Columns to display | `customer_name`, `customer_segment`, `late_rate_pct`, `avg_days_to_pay`, `total_invoice_value` |
|--------------------|------------------------------------------------------------------------------------------------|

**Business insight:** Identifies accounts that consistently miss terms. High late rate + high invoice value = prime candidates for structured collections or early-pay discount programs. Share this table with account managers for relationship-level interventions.

### 4. Cash Flow Forecast Line Chart

**Data source:** `cash_inflow_trends.csv`

| Setting | Value |
|---------|-------|
| Columns | `payment_month` |
| Rows | `cash_inflow` |
| Chart type | Line with trend or moving average |

**Business insight:** Historical cash inflow informs short-term liquidity planning. Use a 3-month moving average as a simple forecast baseline; overlay open AR from aging buckets to estimate near-term collections. Declining inflow with rising outstanding AR signals tightening cash position.

### Dashboard Layout Suggestion

```
┌─────────────────────────────────────────────────────┐
│  KPI Cards: Overall DSO | Open AR | Late Rate %      │
├──────────────────────────┬──────────────────────────┤
│  DSO Trend (line)        │  Cash Inflow (line)      │
├──────────────────────────┴──────────────────────────┤
│  Aging Buckets (stacked bar by segment)            │
├─────────────────────────────────────────────────────┤
│  Top 10 Late Payers (table)                        │
└─────────────────────────────────────────────────────┘
```

### Dashboard Preview

`docs/dashboard.html` is a standalone, self-contained HTML preview of this dashboard (open it directly
in a browser — no server needed) built from the same `/exports` CSVs described above. It exists so the
layout and numbers can be sanity-checked before building the real thing in Tableau. **It is not a
substitute for a published Tableau dashboard** — the CSVs above still need to be imported into Tableau
Desktop/Public and published there to produce an actual Tableau project link.

## Excel Summary Report

`exports/cash_flow_summary.xlsx` includes:

- **Executive Summary** — Overall DSO, open AR, invoice count
- **DSO by Segment** — Segment comparison for leadership reviews
- **Late Rate by Month** — Operational trend for collections teams
- **Aging Buckets** — Dollar exposure by overdue bracket

Designed for ad-hoc business reporting without requiring Tableau access.

## SQL Query Reference

| File | Purpose |
|------|---------|
| `dso_overall.sql` | Portfolio-level DSO |
| `dso_by_segment.sql` | DSO and late rate by segment |
| `dso_by_month.sql` | Monthly DSO trend |
| `late_payment_rate_by_customer.sql` | Ranked late payers |
| `late_payment_rate_by_month.sql` | Monthly late payment rate |
| `aging_buckets.sql` | Outstanding AR aging breakdown |
| `cash_inflow_trends.sql` | Month-over-month cash collections |

## Tech Stack

- Python 3.10+ (pandas, numpy, openpyxl)
- SQLite
- Tableau (dashboard consumption)
- Excel (stakeholder reporting)

## License

MIT

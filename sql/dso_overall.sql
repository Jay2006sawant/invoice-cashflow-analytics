-- Overall Days Sales Outstanding (DSO) as of analysis date.
-- DSO = (Total AR Outstanding / Total Credit Sales) * Days in Period
-- Uses trailing 90-day revenue as the denominator for a rolling view.

WITH params AS (
    SELECT DATE('2026-05-10') AS as_of_date
),
outstanding AS (
    SELECT SUM(invoice_amount) AS total_outstanding_ar
    FROM invoices, params
    WHERE payment_status = 'Outstanding'
),
trailing_sales AS (
    SELECT SUM(invoice_amount) AS credit_sales_90d
    FROM invoices, params
    WHERE DATE(invoice_date) BETWEEN DATE(as_of_date, '-90 days') AND as_of_date
)
SELECT
    ROUND(
        COALESCE(o.total_outstanding_ar, 0)
        / NULLIF(t.credit_sales_90d, 0)
        * 90,
        1
    ) AS dso_days,
    COALESCE(o.total_outstanding_ar, 0) AS total_outstanding_ar,
    (SELECT COUNT(*) FROM invoices) AS invoice_count
FROM outstanding o
CROSS JOIN trailing_sales t;

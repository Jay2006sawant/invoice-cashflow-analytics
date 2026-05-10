-- DSO by customer segment, using the same methodology as dso_overall.sql
-- (Outstanding AR / trailing-90-day sales * 90) so the two figures reconcile.
-- avg_days_to_pay is reported separately as a distinct, genuinely different
-- metric: the average actual settlement time per invoice.
WITH params AS (
    SELECT DATE('2026-05-10') AS as_of_date
),
outstanding AS (
    SELECT customer_segment, SUM(invoice_amount) AS total_outstanding_ar
    FROM invoices, params
    WHERE payment_status = 'Outstanding'
    GROUP BY customer_segment
),
trailing_sales AS (
    SELECT customer_segment, SUM(invoice_amount) AS credit_sales_90d
    FROM invoices, params
    WHERE DATE(invoice_date) BETWEEN DATE(as_of_date, '-90 days') AND as_of_date
    GROUP BY customer_segment
),
settlement AS (
    SELECT customer_segment,
           ROUND(AVG(days_to_pay), 1) AS avg_days_to_pay,
           COUNT(*) AS invoice_count,
           ROUND(AVG(is_late) * 100, 1) AS late_rate_pct
    FROM invoices
    GROUP BY customer_segment
)
SELECT
    s.customer_segment,
    ROUND(
        COALESCE(o.total_outstanding_ar, 0)
        / NULLIF(t.credit_sales_90d, 0)
        * 90,
        1
    ) AS dso_days,
    s.avg_days_to_pay,
    s.invoice_count,
    s.late_rate_pct
FROM settlement s
LEFT JOIN outstanding o ON o.customer_segment = s.customer_segment
LEFT JOIN trailing_sales t ON t.customer_segment = s.customer_segment
ORDER BY dso_days DESC;

-- Monthly DSO trend for Tableau line chart.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', invoice_date) AS invoice_month,
        SUM(invoice_amount) AS monthly_sales,
        AVG(days_to_pay) AS avg_days_to_pay
    FROM invoices
    GROUP BY strftime('%Y-%m', invoice_date)
),
outstanding_by_month AS (
    SELECT
        strftime('%Y-%m', invoice_date) AS invoice_month,
        SUM(CASE WHEN payment_status = 'Outstanding' THEN invoice_amount ELSE 0 END) AS open_ar
    FROM invoices
    GROUP BY strftime('%Y-%m', invoice_date)
)
SELECT
    m.invoice_month,
    ROUND(m.avg_days_to_pay, 1) AS avg_days_to_pay,
    ROUND(m.monthly_sales, 2) AS monthly_sales,
    ROUND(COALESCE(o.open_ar, 0), 2) AS open_ar
FROM monthly m
LEFT JOIN outstanding_by_month o ON m.invoice_month = o.invoice_month
ORDER BY m.invoice_month;

-- Late payment rate by invoice month.
SELECT
    strftime('%Y-%m', invoice_date) AS invoice_month,
    COUNT(*) AS total_invoices,
    SUM(is_late) AS late_invoices,
    ROUND(SUM(is_late) * 100.0 / COUNT(*), 1) AS late_rate_pct,
    ROUND(AVG(days_to_pay), 1) AS avg_days_to_pay
FROM invoices
GROUP BY strftime('%Y-%m', invoice_date)
ORDER BY invoice_month;

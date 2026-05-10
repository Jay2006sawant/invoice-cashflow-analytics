-- Late payment rate ranked by customer (for top-10 late payers Tableau table).
SELECT
    customer_name,
    customer_segment,
    COUNT(*) AS total_invoices,
    SUM(is_late) AS late_invoices,
    ROUND(SUM(is_late) * 100.0 / COUNT(*), 1) AS late_rate_pct,
    ROUND(AVG(days_to_pay), 1) AS avg_days_to_pay,
    ROUND(SUM(invoice_amount), 2) AS total_invoice_value
FROM invoices
GROUP BY customer_name, customer_segment
HAVING COUNT(*) >= 5
ORDER BY late_rate_pct DESC, avg_days_to_pay DESC
LIMIT 10;

-- Aging bucket breakdown for outstanding invoices (collections focus areas).
SELECT
    CASE
        WHEN days_overdue BETWEEN 0 AND 30 THEN '0-30 days'
        WHEN days_overdue BETWEEN 31 AND 60 THEN '31-60 days'
        WHEN days_overdue BETWEEN 61 AND 90 THEN '61-90 days'
        WHEN days_overdue > 90 THEN '90+ days'
        ELSE 'Current (not yet due)'
    END AS aging_bucket,
    customer_segment,
    COUNT(*) AS invoice_count,
    ROUND(SUM(invoice_amount), 2) AS outstanding_amount
FROM invoices
WHERE payment_status = 'Outstanding'
GROUP BY aging_bucket, customer_segment
ORDER BY
    CASE aging_bucket
        WHEN 'Current (not yet due)' THEN 1
        WHEN '0-30 days' THEN 2
        WHEN '31-60 days' THEN 3
        WHEN '61-90 days' THEN 4
        ELSE 5
    END,
    customer_segment;

-- Month-over-month cash inflow from paid and late-settled invoices.
SELECT
    strftime('%Y-%m', payment_date) AS payment_month,
    COUNT(*) AS payment_count,
    ROUND(SUM(invoice_amount), 2) AS cash_inflow,
    ROUND(AVG(days_to_pay), 1) AS avg_days_to_pay
FROM invoices
WHERE payment_date IS NOT NULL
GROUP BY strftime('%Y-%m', payment_date)
ORDER BY payment_month;

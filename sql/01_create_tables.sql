-- Create invoices table for cleaned invoice payment data.
DROP TABLE IF EXISTS invoices;

CREATE TABLE invoices (
    invoice_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_segment TEXT NOT NULL CHECK (customer_segment IN ('SMB', 'Mid-Market', 'Enterprise')),
    vendor_name TEXT NOT NULL,
    invoice_amount REAL NOT NULL CHECK (invoice_amount > 0),
    invoice_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    payment_date TEXT,
    payment_status TEXT NOT NULL CHECK (payment_status IN ('Paid', 'Late', 'Outstanding')),
    days_to_pay INTEGER,
    is_late INTEGER NOT NULL CHECK (is_late IN (0, 1)),
    days_overdue INTEGER
);

CREATE INDEX idx_invoices_customer ON invoices(customer_name);
CREATE INDEX idx_invoices_segment ON invoices(customer_segment);
CREATE INDEX idx_invoices_invoice_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_payment_status ON invoices(payment_status);

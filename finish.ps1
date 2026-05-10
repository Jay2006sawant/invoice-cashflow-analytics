$ErrorActionPreference = "Stop"

# Run this script from inside the project root (invoice-cashflow-analytics/).
# It rebuilds the database + exports, then commits and pushes to GitHub.

python scripts/setup_database.py
python scripts/export_reports.py

if (-not (Test-Path .git)) { git init }
git remote remove origin 2>$null
git remote add origin https://github.com/Jay2006sawant/invoice-cashflow-analytics.git

git add .
git commit -m "Add invoice cash flow analytics dashboard"
git branch -M main
git push -u origin main

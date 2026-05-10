"""
Create SQLite database, load cleaned invoices, and run analytics queries.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "database" / "invoices.db"
CLEAN_PATH = PROJECT_ROOT / "data" / "invoices_cleaned.csv"
SQL_DIR = PROJECT_ROOT / "sql"


def run_sql_file(conn: sqlite3.Connection, path: Path) -> pd.DataFrame | None:
    sql = path.read_text(encoding="utf-8")
    if sql.strip().upper().startswith("SELECT"):
        return pd.read_sql_query(sql, conn)
    conn.executescript(sql)
    return None


def load_cleaned_data(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(CLEAN_PATH)
    df.to_sql("invoices", conn, if_exists="replace", index=False)
    print(f"Loaded {len(df):,} rows into invoices table.")


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    create_script = SQL_DIR / "01_create_tables.sql"
    run_sql_file(conn, create_script)
    load_cleaned_data(conn)

    query_files = sorted(SQL_DIR.glob("*.sql"))
    for query_file in query_files:
        if query_file.name == "01_create_tables.sql":
            continue
        result = run_sql_file(conn, query_file)
        if result is not None:
            print(f"\n--- {query_file.name} ({len(result)} rows) ---")
            print(result.head())

    conn.close()
    print(f"\nDatabase ready at {DB_PATH}")


if __name__ == "__main__":
    main()

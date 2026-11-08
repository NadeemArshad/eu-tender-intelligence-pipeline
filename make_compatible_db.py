import duckdb
from pathlib import Path

# Find the data folder
data_folder = Path(__file__).parent / "data"

# Original database - we will NOT modify it
source = data_folder / "tenders.duckdb"

# New database compatible with older DuckDB versions
target = data_folder / "tenders_dbt_refresh.duckdb"
# Safety checks
if not source.exists():
    raise SystemExit("Original database not found!")

if target.exists():
    raise SystemExit("Compatible database already exists!")

# Use Windows-compatible file paths
source_path = source.as_posix().replace("'", "''")
target_path = target.as_posix().replace("'", "''")

# Connect to an in-memory DuckDB database
connection = duckdb.connect()

try:
    # Open the existing database without changing it
    connection.execute(
        f"ATTACH '{source_path}' AS original (READ_ONLY)"
    )

    # Create a new database using the older storage format
    connection.execute(
        f"ATTACH '{target_path}' AS compatible "
        "(STORAGE_VERSION 'v1.5.0')"
    )

    # Copy database tables and data
    connection.execute(
        "COPY FROM DATABASE original TO compatible"
    )

    # Verify the tender records
    total = connection.execute("""
        SELECT COUNT(*)
        FROM compatible.main.tender_notices
    """).fetchone()[0]

    print("Compatible database created successfully!")
    print("Total tenders copied:", total)

finally:
    connection.close()
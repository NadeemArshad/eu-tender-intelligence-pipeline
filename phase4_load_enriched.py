import csv
import json
import duckdb

from pathlib import Path

# Step 1: Define file paths
data_folder = Path(__file__).parent / "data"

csv_path = data_folder / "tenders_enriched.csv"
db_path = data_folder / "tenders.duckdb"

# Check that files exist
if not csv_path.exists():
    raise SystemExit("Enriched CSV file not found!")

if not db_path.exists():
    raise SystemExit("DuckDB database not found!")

# Step 2: Connect to DuckDB
connection = duckdb.connect(str(db_path))

print("Successfully connected to DuckDB!")

# Step 3: Create enrichment table
connection.execute("""
    CREATE TABLE IF NOT EXISTS tender_enrichment (
        notice_number VARCHAR PRIMARY KEY,
        cpv_codes_json VARCHAR,
        deadline_dates_json VARCHAR,
        deadline_times_json VARCHAR,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

print("Enrichment table is ready!")

# Step 4: Initialize counters
new_count = 0
updated_count = 0
unchanged_count = 0
skipped_count = 0

# Step 5: Read and load CSV
try:
    connection.execute("BEGIN TRANSACTION")

    with open(csv_path, newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        required_columns = [
            "notice_number",
            "cpv_codes_json",
            "deadline_dates_json",
            "deadline_times_json"
        ]

        if not set(required_columns).issubset(reader.fieldnames or []):
            raise ValueError("Required CSV columns are missing!")

        for row in reader:

            number = (row["notice_number"] or "").strip()

            if not number:
                skipped_count += 1
                continue

            # Preserve original JSON values
            incoming_values = (
                row["cpv_codes_json"],
                row["deadline_dates_json"],
                row["deadline_times_json"]
            )

            # Validate JSON format
            for value in incoming_values:
                parsed = json.loads(value)

                if parsed is not None and not isinstance(parsed, list):
                    raise ValueError(
                        f"Unexpected JSON structure for {number}"
                    )

            # Verify that the tender exists
            parent = connection.execute("""
                SELECT notice_number
                FROM tender_notices
                WHERE notice_number = ?
            """, [number]).fetchone()

            if parent is None:
                raise ValueError(
                    f"Tender {number} missing from tender_notices"
                )

            # Compare with existing enrichment record
            existing = connection.execute("""
                SELECT
                    cpv_codes_json,
                    deadline_dates_json,
                    deadline_times_json
                FROM tender_enrichment
                WHERE notice_number = ?
            """, [number]).fetchone()

            if existing == incoming_values:
                unchanged_count += 1
                continue

            if existing is None:
                new_count += 1
            else:
                updated_count += 1

            # Insert or update enrichment information
            connection.execute("""
                INSERT INTO tender_enrichment (
                    notice_number,
                    cpv_codes_json,
                    deadline_dates_json,
                    deadline_times_json
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT (notice_number)
                DO UPDATE SET
                    cpv_codes_json = EXCLUDED.cpv_codes_json,
                    deadline_dates_json = EXCLUDED.deadline_dates_json,
                    deadline_times_json = EXCLUDED.deadline_times_json,
                    updated_at = NOW()

            """, [number, *incoming_values])

    connection.execute("COMMIT")

    # Step 6: Display results
    total = connection.execute("""
        SELECT COUNT(*)
        FROM tender_enrichment
    """).fetchone()[0]

    print("\nEnrichment loading completed!")
    print("New records:", new_count)
    print("Updated records:", updated_count)
    print("Unchanged records:", unchanged_count)
    print("Skipped records:", skipped_count)
    print("Total enrichment records:", total)

except Exception:
    connection.execute("ROLLBACK")
    raise

finally:
    connection.close()
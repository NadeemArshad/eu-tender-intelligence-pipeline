import sys
import csv
import duckdb
from pathlib import Path

# Step 1: Find the data folder
data_folder = Path(__file__).parent / "data"

# Step 2: Connect to DuckDB
connection = duckdb.connect(str(data_folder / "tenders.duckdb"))

print("Successfully connected to DuckDB!")

# Step 3: Create the table
connection.execute("""
    CREATE TABLE IF NOT EXISTS tender_notices (
        notice_number VARCHAR PRIMARY KEY,
        publication_date VARCHAR,
        title VARCHAR,
        buyer VARCHAR,
        country VARCHAR,
        notice_type VARCHAR,
        link VARCHAR
    )
""")

print("Table tender_notices created successfully!")

# Step 4: Check that the table exists
tables = connection.execute("SHOW TABLES").fetchall()

print("Tables in database:", tables)

# Step 5: Find the CSV file
# Select the CSV file to load
use_paginated = "--paginated" in sys.argv

if use_paginated:
    csv_path = data_folder / "tenders_paginated.csv"
else:
    csv_path = data_folder / "tenders.csv"

print("Loading data from:", csv_path.name)

# Step 6: Initialize counters
new_count = 0
updated_count = 0
unchanged_count = 0

# Step 7: Read the CSV file
with open(csv_path, newline="", encoding="utf-8-sig") as file:

    reader = csv.DictReader(file)

    print("CSV columns:", reader.fieldnames)

    for row in reader:

        # Skip records without a tender number
        if not row["notice_number"]:
            continue

        # Get incoming CSV values
        incoming_values = (
            row["date"],
            row["title"],
            row["buyer"],
            row["country"],
            row["type"],
            row["link"]
        )

        # Check whether the tender already exists
        existing_values = connection.execute("""
            SELECT
                publication_date,
                title,
                buyer,
                country,
                notice_type,
                link
            FROM tender_notices
            WHERE notice_number = ?
        """, [row["notice_number"]]).fetchone()

        # Step 8: Classify the tender
        if existing_values is None:
            new_count += 1

        elif existing_values == incoming_values:
            unchanged_count += 1
            continue

        else:
            updated_count += 1

        # Step 9: Insert new or update existing tenders
        connection.execute("""
            INSERT INTO tender_notices (
                notice_number,
                publication_date,
                title,
                buyer,
                country,
                notice_type,
                link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT (notice_number)
            DO UPDATE SET
                publication_date = EXCLUDED.publication_date,
                title = EXCLUDED.title,
                buyer = EXCLUDED.buyer,
                country = EXCLUDED.country,
                notice_type = EXCLUDED.notice_type,
                link = EXCLUDED.link
        """, [
            row["notice_number"],
            row["date"],
            row["title"],
            row["buyer"],
            row["country"],
            row["type"],
            row["link"]
        ])

print("Tender data loaded successfully!")

# Step 10: Count total records
total = connection.execute("""
    SELECT COUNT(*)
    FROM tender_notices
""").fetchone()[0]

print("Total tenders in DuckDB:", total)

# Step 11: Display the first 5 tenders
results = connection.execute("""
    SELECT
        notice_number,
        title,
        buyer,
        country
    FROM tender_notices
    LIMIT 5
""").fetchall()

print("\nFirst 5 tenders in the database:")

for tender in results:
    print(tender)

# Step 12: Check duplicate notice numbers
duplicates = connection.execute("""
    SELECT
        notice_number,
        COUNT(*) AS total
    FROM tender_notices
    GROUP BY notice_number
    HAVING COUNT(*) > 1
""").fetchall()

print("Duplicate notice numbers:", duplicates)

# Step 13: Check whether the UPSERT test title remains
result = connection.execute("""
    SELECT notice_number, title
    FROM tender_notices
    WHERE title LIKE ?
""", ["%UPSERT TEST UPDATED%"]).fetchall()

print("Updated tender:", result)

# Step 14: Display pipeline summary
print("\nPipeline execution summary:")
print("New tenders:", new_count)
print("Updated tenders:", updated_count)
print("Unchanged tenders:", unchanged_count)

# Step 15: Close the connection
connection.close()

print("\nPipeline completed successfully!")
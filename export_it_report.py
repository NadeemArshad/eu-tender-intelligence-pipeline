import csv
import duckdb
from pathlib import Path

# Step 1: Define the file paths
project = Path(__file__).resolve().parent

database = project / "data" / "tenders_dbt_refresh.duckdb"
output_folder = project / "data" / "exports"

output_folder.mkdir(parents=True, exist_ok=True)

# Step 2: Check the database
if not database.exists():
    raise SystemExit("Reporting database not found!")

# Step 3: Connect without changing the database
connection = duckdb.connect(
    str(database),
    read_only=True
)

# Step 4: Choose the report columns
columns = """
    notice_number,
    published_on,
    title,
    buyer,
    country,
    match_source,
    matching_it_cpv_codes,
    candidate_deadline_date,
    candidate_deadline_time,
    deadline_review_status,
    days_until_candidate_deadline,
    opportunity_review_status,
    ted_link
"""

# Step 5: Make CSV text safer to open in Excel
def safe_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(
        ("=", "+", "-", "@", "\t", "\r")
    ):
        return "'" + value
    return value


# Step 6: Define an export function
def export_csv(query, filename):

    result = connection.execute(query)

    headers = [column[0] for column in result.description]
    rows = result.fetchall()

    file_path = output_folder / filename

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(headers)

        for row in rows:
            writer.writerow([safe_cell(value) for value in row])

    print(f"{filename}: {len(rows)} records exported")

    return len(rows)


try:

    # Step 7: Export every IT tender candidate
    all_query = f"""
        SELECT {columns}
        FROM analytics.mart_it_tender_report
        ORDER BY
            published_on DESC NULLS LAST,
            notice_number
    """

    all_count = export_csv(
        all_query,
        "all_it_tenders.csv"
    )

    # Step 8: Export CPV-matched tenders for priority review
    priority_query = f"""
        SELECT {columns}
        FROM analytics.mart_it_tender_report

        WHERE match_source IN (
            'CPV only',
            'CPV and title'
        )

        AND candidate_deadline_date >= CURRENT_DATE

        AND deadline_review_status =
            'Single date/time - verify notice'

        ORDER BY
            candidate_deadline_date ASC,
            notice_number
    """

    priority_count = export_csv(
        priority_query,
        "priority_it_tenders.csv"
    )

    print("\nEXPORT COMPLETED SUCCESSFULLY!")
    print("All IT tender candidates:", all_count)
    print("Priority review candidates:", priority_count)
    print("Output folder:", output_folder)

finally:
    connection.close()
"""Download recent Dutch procurement notices from the EU TED API."""

import csv
import json
from datetime import date, timedelta
from pathlib import Path

import requests


# Step 1: API configuration
API_URL = "https://api.ted.europa.eu/v3/notices/search"

# Search notices published within the last 7 days
# Step 14B: Read the last successful checkpoint
checkpoint_file = Path(__file__).parent / "data" / "checkpoint.json"

if checkpoint_file.exists():

    checkpoint = json.loads(
        checkpoint_file.read_text(encoding="utf-8")
    )

    last_successful_date = date.fromisoformat(
        checkpoint["last_successful_date"]
    )

    # Recheck the previous 7 days for late-arriving notices
    start_date = last_successful_date - timedelta(days=7)

else:
    # First run: no checkpoint exists
    start_date = date.today() - timedelta(days=7)

QUERY = (
    f"buyer-country=NLD AND "
    f"publication-date>={start_date.strftime('%Y%m%d')} "
    "SORT BY publication-date DESC"
)

FIELDS = [
    "publication-number",
    "publication-date",
    "notice-title",
    "buyer-name",
    "buyer-country",
    "notice-type",
    "classification-cpv",
    "deadline-receipt-tender-date-lot",
    "deadline-receipt-tender-time-lot",
]


# Step 2: Convert API values to text
def as_text(value):
    """Convert translations and lists into readable text."""

    if value is None:
        return ""

    if isinstance(value, dict):
        for language in ("eng", "nld", "mul"):
            if language in value:
                return as_text(value[language])

        return as_text(next(iter(value.values()), ""))

    if isinstance(value, list):
        return "; ".join(as_text(item) for item in value)

    return str(value)


# Step 3: Main pipeline
def main():

    print("Connecting to EU TED...")

    all_notices = []
    raw_pages = []

    # Step 4: Pagination settings
    PAGE_SIZE = 100
    MAX_PAGES = 50
    download_complete = False

    # Step 5: Download pages
    for page_number in range(1, MAX_PAGES + 1):

        payload = {
            "query": QUERY,
            "fields": FIELDS,
            "page": page_number,
            "limit": PAGE_SIZE,
            "scope": "ALL",
            "paginationMode": "PAGE_NUMBER"
        }

        try:
            response = requests.post(
                API_URL,
                json=payload,
                timeout=45
            )

            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError) as error:
            print(f"Page {page_number} failed:", error)
            raise SystemExit(1)

        # Step 6: Read the API response
        notices = data.get("notices")

        if not isinstance(notices, list) or data.get("timedOut") is True:
            print("Unexpected or incomplete API response.")
            raise SystemExit(1)

        print(
            f"Page {page_number}: "
            f"{len(notices)} notices received"
        )

        # Stop if the page is empty
        if not notices:
            download_complete = True
            break

        # Add notices to the combined list
        all_notices.extend(notices)

        # Step 7: Save the original API response
        raw_pages.append({
            "page": page_number,
            "response": data
        })

        # Step 8: Detect the last page
        if len(notices) < PAGE_SIZE:
            download_complete = True
            print("All available pages downloaded.")
            break

    # Step 9: Check download completeness
    if not download_complete:
        print("WARNING: Maximum page limit reached.")
        print("Download may be incomplete.")
        print("Existing output files will not be replaced.")
        raise SystemExit(1)

    # Step 10: Create output folder
    output_folder = Path(__file__).parent / "data"
    output_folder.mkdir(exist_ok=True)

    # Step 11: Save raw JSON
    raw_file = output_folder / "raw_notices_paginated.json"

    raw_file.write_text(
        json.dumps(raw_pages, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Step 12: Create CSV output
    csv_file = output_folder / "tenders_paginated.csv"

    seen = set()

    with csv_file.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "notice_number",
            "date",
            "title",
            "buyer",
            "country",
            "type",
            "link"
        ])

        # Step 13: Convert notices into CSV rows
        for item in all_notices:

            number = as_text(item.get("publication-number"))

            # Skip empty or duplicate notice numbers
            if not number or number in seen:
                continue

            seen.add(number)

            writer.writerow([
                number,
                as_text(item.get("publication-date")),
                as_text(item.get("notice-title")),
                as_text(item.get("buyer-name")),
                as_text(item.get("buyer-country")),
                as_text(item.get("notice-type")),
                f"https://ted.europa.eu/en/notice/-/detail/{number}"
            ])
        # Save additional procurement fields
    enriched_file = output_folder / "tenders_enriched.csv"

    seen_enriched = set()

    with enriched_file.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "notice_number",
            "cpv_codes_json",
            "deadline_dates_json",
            "deadline_times_json"
        ])

        for item in all_notices:

            number = as_text(item.get("publication-number"))

            if not number or number in seen_enriched:
                continue

            seen_enriched.add(number)

            writer.writerow([
                number,
                json.dumps(
                    item.get("classification-cpv"),
                    ensure_ascii=False
                ),
                json.dumps(
                    item.get("deadline-receipt-tender-date-lot"),
                    ensure_ascii=False
                ),
                json.dumps(
                    item.get("deadline-receipt-tender-time-lot"),
                    ensure_ascii=False
                )
            ])

    print("Enriched CSV file:", enriched_file.name)
    # Step 14: Display results
    print("\nPipeline execution completed!")
    print("Unique tenders saved:", len(seen))
    print("CSV file:", csv_file.name)
    print("Raw JSON file:", raw_file.name)


# Step 15: Execute the main function
if __name__ == "__main__":
    main()
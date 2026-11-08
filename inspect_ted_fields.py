import json
import requests

from main import API_URL, QUERY

# Fields we want to inspect
fields = [
    "publication-number",
    "notice-title",
    "classification-cpv",
    "deadline-receipt-tender-date-lot",
    "deadline-receipt-tender-time-lot"
]

# Request only 3 notices
payload = {
    "query": QUERY,
    "fields": fields,
    "page": 1,
    "limit": 3,
    "scope": "ALL",
    "paginationMode": "PAGE_NUMBER"
}

print("Inspecting TED tender fields...")

response = requests.post(
    API_URL,
    json=payload,
    timeout=45
)

response.raise_for_status()

data = response.json()

notices = data.get("notices", [])

print("Notices received:", len(notices))

for notice in notices:

    print("\n------------------------")
    print("TENDER RECORD")
    print("------------------------")

    for field in fields:

        value = notice.get(field)

        print("\nField:", field)
        print(json.dumps(
            value,
            indent=2,
            ensure_ascii=False
        ))
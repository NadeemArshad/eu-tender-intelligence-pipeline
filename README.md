# EU Tender Intelligence — Easy VS Code Starter

This is **Phase 1** of a real open-source Data Engineering project. It downloads the **10 most recently published** procurement notices from buyers in the Netherlands, using the **official EU TED Search API**. It saves two files:

- `data/raw_notices.json` — original API response and request
- `data/tenders.csv` — a simple table that Excel and VS Code can open

No Azure account, API key, or paid software is required.

## Steps in VS Code (Windows)

1. Extract the ZIP and open the folder **eu-tenders-vscode-simple** in VS Code: **File → Open Folder**.
2. Open **Terminal → New Terminal**.
3. Check Python: `py --version` (install Python if Windows doesn't find it).
4. Install Requests: `py -m pip install requests`
5. Run: `py main.py`
6. Click `data/tenders.csv` and `data/raw_notices.json` in the VS Code file explorer.

> If `py` is not recognized but `python` is available, substitute `python` for `py` in the commands.

### What does each part do?
- **API**: A service where our program requests information from TED.
- **Python**: The language that contacts the API and saves the result.
- **JSON**: The original structured data from the source.
- **CSV**: The simplified table for humans or later warehouse processing.

## Important limits

This starter fetches **only the first 10 results** and overwrites the two output files each run. It is deliberately a small teaching example, **not yet an incremental data pipeline**. Later phases will add DuckDB, full pagination, history, dbt transformations and Dagster orchestration.

Source documentation: https://docs.ted.europa.eu/api/latest/search.html
Data source: EU Publications Office / TED. Not affiliated with TED.

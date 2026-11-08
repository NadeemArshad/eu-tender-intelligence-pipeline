# EU Tender Intelligence Pipeline

An end-to-end Data Engineering portfolio project that collects public European procurement notices, processes them with Python and DuckDB, transforms them using dbt, and generates business-readable IT tender opportunity reports.

## Project Overview

Organizations searching for public IT contracts often need to review large numbers of procurement notices.

This project demonstrates how an automated data pipeline can:

- Retrieve public tender information from the EU TED API.
- Load records incrementally into DuckDB.
- Extract CPV classification codes and reported deadlines.
- Identify IT opportunities using both CPV codes and title keywords.
- Apply automated data-quality tests.
- Export CSV reports for further business review.

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | API extraction and orchestration |
| TED Search API | Public procurement data |
| DuckDB | Analytical data storage |
| dbt | SQL transformations and testing |
| Git | Version control |
| CSV / Excel | Business-readable reports |

## Architecture

```text
EU TED Search API
       |
       v
Python Extraction (main.py)
       |
       v
Raw JSON and CSV Files
       |
       v
DuckDB Incremental Loading
       |
       v
CPV and Deadline Enrichment
       |
       v
Compatible Reporting Database
       |
       v
dbt Transformations and Tests
       |
       v
IT Opportunity Reporting Mart
       |
       v
CSV Export
       |
       +-- all_it_tenders.csv
       |
       +-- priority_it_tenders.csv
```

## Key Features

### Incremental Data Loading

Tender notices are compared against previously stored records.

The pipeline identifies new, changed and unchanged records, reducing unnecessary updates.

### CPV-Based Classification

Official procurement classification codes are combined with title-based matching to identify potential IT opportunities.

### Deadline Review

Reported submission dates are extracted and evaluated.

Missing or multiple values are flagged for review. Candidate deadlines are not treated as confirmation that a tender is still accepting submissions.

### Automated Data Quality

dbt tests validate important conditions such as unique notice identifiers, non-null identifiers, matching classifications and deadline extraction rules.

### Automated Reporting

The pipeline generates two CSV files:

- `all_it_tenders.csv`: All identified IT tender candidates.
- `priority_it_tenders.csv`: CPV-matched candidates with future reported deadline dates that require source verification.

## Example Results

Results from a successful local pipeline execution on November 6, 2026:

| Metric | Result |
|--------|--------|
| IT tender candidates | 145 |
| Priority review candidates | 61 |
| Pipeline execution | Successful |
| CSV reports generated | 2 |

These numbers represent a historical pipeline run, not live tender availability.

## Running the Pipeline

The project was developed on Windows using Python 3.13, DuckDB and dbt OSS with DuckDB support.

A compatible local Python environment and dbt executable are required.

The local dbt profile is stored at:

`dbt_tenders/profiles.yml`

It is excluded from Git because it contains local environment configuration.

The pipeline currently expects dbt at:

`.venv-dbt/Scripts/dbt.exe`

Run the complete workflow from the project root:

```powershell
py run_full_pipeline.py
```

Successful execution performs extraction, loading, enrichment, dbt transformations, tests, reporting database publication and CSV export.

Generated reports are stored in:

`data/exports/`

The local `data/` directory and virtual environments are excluded from version control.

## Main Project Files

| File | Purpose |
|------|---------|
| main.py | Retrieves TED notices |
| phase2_load.py | Loads tender records into DuckDB |
| phase4_load_enriched.py | Loads CPV and deadline data |
| run_full_pipeline.py | Orchestrates the complete workflow |
| export_it_report.py | Generates CSV reports |
| dbt_tenders/models/ | SQL transformation models |
| dbt_tenders/tests/ | Custom data-quality tests |

## Current Limitations

- The pipeline currently focuses on Dutch procurement notices.
- CPV and title matching produces candidate opportunities, not guaranteed relevance.
- Lot-specific deadline relationships require additional modelling.
- Submission status must be checked against the original TED notice.
- The current setup uses local execution rather than a cloud scheduler.
- Dependency pinning and one-command environment setup are planned improvements.

## Data Source

Tender data originates from the European Union's Tenders Electronic Daily (TED) service.

This repository contains source code and transformations, not a continuously maintained public tender database.

## Project Purpose

This project demonstrates practical Data Engineering capabilities in API integration, incremental data ingestion, analytical modelling, data quality and reporting automation.

It is a portfolio demonstration, not an official EU procurement service.


### Detailed Architecture

[View the complete pipeline architecture](docs/architecture.md)

A sample dbt connection configuration is available in
`dbt_tenders/profiles.example.yml`.

Copy the example to `dbt_tenders/profiles.yml` when setting up
a new local environment. The actual profile is excluded from Git.

### Installation on Windows

Use Python 3.13.

Create an environment for Python ingestion and reporting:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a separate environment for dbt OSS:

```powershell
py -3.13 -m venv .venv-dbt
.\.venv-dbt\Scripts\python.exe -m pip install -r requirements-dbt.txt
```

Create the local dbt profile:

```powershell
Copy-Item dbt_tenders\profiles.example.yml dbt_tenders\profiles.yml
```

Run the complete pipeline from the project root:

```powershell
.\.venv\Scripts\python.exe run_full_pipeline.py
```

An internet connection is required to retrieve TED notices.
dbt may also download its database driver on first use.

The pipeline generates data and reporting files locally.
These files are excluded from Git.

# EU Tender Intelligence — System Architecture

This diagram shows the automated flow from public EU procurement data to validated IT tender reports.

```mermaid
flowchart TD
    A["EU TED Search API"] --> B["main.py: Extract and paginate"]

    B --> C["Tender CSV"]
    B --> D["CPV and deadline CSV"]

    C --> E["phase2_load.py"]
    D --> F["phase4_load_enriched.py"]

    E --> G[("DuckDB: tender data")]
    F --> G

    G --> H["Create compatible database snapshot"]
    H --> I["dbt staging, intermediate and marts"]
    I --> J["dbt models and quality tests"]

    J --> K{"All checks pass?"}

    K -->|No| X["Stop and report error"]
    K -->|Yes| L["Publish reporting database"]

    L --> M["export_it_report.py"]

    M --> N["all_it_tenders.csv"]
    M --> O["priority_it_tenders.csv"]

    M --> P{"Exports successful?"}

    P -->|Yes| Q["Save successful checkpoint"]
    P -->|No| X
```

## Data Processing

1. Python retrieves public procurement notices from TED.
2. DuckDB stores tender records and enrichment data.
3. A compatible database snapshot is prepared for dbt.
4. dbt transforms the data and runs automated tests.
5. The validated reporting database is published.
6. Python exports IT opportunity reports.
7. The checkpoint is updated after successful execution.

## Reliability Considerations

- Tender records are compared with existing records to reduce unnecessary updates.
- dbt tests check selected integrity and business rules.
- The published database is updated only after a successful dbt build.
- Reports require manual verification of tender availability and lot-level deadlines.
- Database and CSV publication are not yet fully transactional.
```
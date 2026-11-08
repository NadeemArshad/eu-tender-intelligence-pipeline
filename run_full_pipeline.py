import json
import os
import subprocess
import sys

from datetime import date
from pathlib import Path
from uuid import uuid4

import duckdb


# Step 1: Define project paths
project = Path(__file__).resolve().parent
data = project / "data"

source = data / "tenders.duckdb"
published = data / "tenders_dbt_refresh.duckdb"

# Create a unique temporary database
# Temporary folder for building the new database
# Temporary folder for building the new database
candidate_dir = data / f"candidate_{uuid4().hex[:8]}"

candidate_dir.mkdir(parents=True, exist_ok=False)

# Keep the database filename consistent
candidate = candidate_dir / "tenders_dbt_refresh.duckdb"

# dbt executable location
dbt_exe = project / ".venv-dbt" / "Scripts" / "dbt.exe"


# Step 2: Helper function for DuckDB file paths
def sql_path(path):
    return path.as_posix().replace("'", "''")


# Track whether the new reporting database was published
published_updated = False


try:

    # STEP 3: Download tender data
    print("STEP 1: Downloading EU tender data...", flush=True)

    subprocess.run(
        [sys.executable, str(project / "main.py")],
        cwd=project,
        check=True
    )

    # STEP 4: Load tender data into DuckDB
    print("STEP 2: Loading tenders into DuckDB...", flush=True)

    subprocess.run(
        [
            sys.executable,
            str(project / "phase2_load.py"),
            "--paginated"
        ],
        cwd=project,
        check=True
    )

        # Load CPV codes and deadlines into DuckDB
    print("Loading enriched tender data...", flush=True)

    subprocess.run(
        [sys.executable, str(project / "phase4_load_enriched.py")],
        cwd=project,
        check=True
    )
    # STEP 5: Create compatible database snapshot
    print("STEP 3: Creating dbt database snapshot...", flush=True)

    connection = duckdb.connect()

    try:

        # Attach original database in read-only mode
        connection.execute(
            f"ATTACH '{sql_path(source)}' AS original (READ_ONLY)"
        )

        # Create database with compatible storage version
        connection.execute(
            f"ATTACH '{sql_path(candidate)}' AS snapshot "
            "(STORAGE_VERSION 'v1.5.0')"
        )

        # Copy all data to compatible database
        connection.execute(
            "COPY FROM DATABASE original TO snapshot"
        )

        # Count original records
        source_count = connection.execute("""
            SELECT COUNT(*)
            FROM original.main.tender_notices
        """).fetchone()[0]

        # Count copied records
        copy_count = connection.execute("""
            SELECT COUNT(*)
            FROM snapshot.main.tender_notices
        """).fetchone()[0]

        # Verify that records match
        if source_count != copy_count:
            raise RuntimeError(
                "Database row counts do not match!"
            )

        print("Records copied:", copy_count)

    finally:
        connection.close()

    # STEP 6: Run dbt models and tests
    print("STEP 4: Running dbt models and tests...", flush=True)

    environment = os.environ.copy()

    environment["DBT_TENDER_DB_PATH"] = str(candidate)

    subprocess.run(
        [str(dbt_exe), "build"],
        cwd=project / "dbt_tenders",
        env=environment,
        check=True
    )

    # STEP 7: Publish reporting database
    print("STEP 5: Publishing reporting database...", flush=True)

    candidate.replace(published)
    candidate_dir.rmdir()
    published_updated = True
        # STEP 6: Export client-ready reports
    print(
        "STEP 6: Exporting IT tender reports...",
        flush=True
    )

    subprocess.run(
        [sys.executable, str(project / "export_it_report.py")],
        cwd=project,
        check=True
    )

    print(
        "IT tender reports exported successfully!",
        flush=True
    )

    # STEP 8: Save checkpoint after successful pipeline
    print("STEP 6: Saving checkpoint...", flush=True)

    checkpoint_file = data / "checkpoint.json"

    checkpoint_data = {
        "last_successful_date": date.today().isoformat()
    }

    temporary_file = checkpoint_file.with_suffix(".json.tmp")

    temporary_file.write_text(
        json.dumps(checkpoint_data, indent=2),
        encoding="utf-8"
    )

    temporary_file.replace(checkpoint_file)

    print("Checkpoint saved successfully!")
    print("Last successful date:", checkpoint_data["last_successful_date"])

    # STEP 9: Final success message
    print("\nFULL PIPELINE COMPLETED SUCCESSFULLY!")
    print("Reporting database:", published.name)


except Exception as error:

    print("\nPIPELINE FAILED:", error)

    if published_updated:
        print(
            "Reporting database was published, "
            "but a later step failed. Check the checkpoint."
        )
    else:
        print(
            "Previous reporting database has been preserved."
        )

    raise SystemExit(1)
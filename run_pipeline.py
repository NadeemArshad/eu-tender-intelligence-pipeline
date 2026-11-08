import json
import subprocess
import sys

from datetime import date
from pathlib import Path

# Project folder
project_folder = Path(__file__).parent

# Checkpoint location
checkpoint_file = project_folder / "data" / "checkpoint.json"

# Step 1: Download tender data
print("STEP 1: Downloading new tender data...")

subprocess.run(
    [sys.executable, "main.py"],
    cwd=project_folder,
    check=True
)

# Step 2: Load data into DuckDB
print("STEP 2: Loading data into DuckDB...")

subprocess.run(
    [sys.executable, "phase2_load.py", "--paginated"],
    cwd=project_folder,
    check=True
)

# Step 3: Save checkpoint after successful processing
checkpoint_data = {
    "last_successful_date": date.today().isoformat()
}

temporary_file = checkpoint_file.with_suffix(".json.tmp")

temporary_file.write_text(
    json.dumps(checkpoint_data, indent=2),
    encoding="utf-8"
)

temporary_file.replace(checkpoint_file)

print("\nCheckpoint saved successfully!")
print("Last successful date:", checkpoint_data["last_successful_date"])
print("Complete pipeline finished!")
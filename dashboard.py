from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# Dashboard configuration
st.set_page_config(
    page_title="EU Tender Intelligence",
    page_icon="📊",
    layout="wide"
)

# Locate the exported reports
project = Path(__file__).resolve().parent

export_dir = project / "data" / "exports"

all_file = export_dir / "all_it_tenders.csv"
priority_file = export_dir / "priority_it_tenders.csv"

st.title("EU Tender Intelligence Dashboard")

st.caption(
    "Public procurement intelligence powered by "
    "Python, DuckDB, dbt and the EU TED API."
)

st.warning(
    "Tender classifications and deadlines require "
    "verification against the official TED notice. "
    "Future candidate deadlines do not confirm "
    "that submissions are still accepted."
)

# Check the reports are available
if not all_file.exists():
    st.error(
        "Report not found. Run run_full_pipeline.py first."
    )
    st.stop()

# Load data
df = pd.read_csv(
    all_file,
    encoding="utf-8-sig",
    dtype=str
).fillna("")
# Show when the CSV file was last modified
last_modified = datetime.fromtimestamp(
    all_file.stat().st_mtime
)

st.caption(
    "Report file last updated (computer local time): "
    + last_modified.strftime("%d %B %Y, %H:%M")
)

if priority_file.exists():
    priority_df = pd.read_csv(
        priority_file,
        encoding="utf-8-sig",
        dtype=str
    )
    priority_count = len(priority_df)
else:
    priority_count = 0
    st.info("Priority report not found.")

# Dashboard filters
st.sidebar.header("Filters")

search = st.sidebar.text_input(
    "Search tender, buyer or notice number"
)

match_options = sorted(
    df["match_source"].unique().tolist()
)

selected_matches = st.sidebar.multiselect(
    "Matching method",
    options=match_options,
    default=match_options
)

status_options = sorted(
    df["deadline_review_status"].unique().tolist()
)

selected_status = st.sidebar.selectbox(
    "Deadline review status",
    options=["All"] + status_options
)

# Apply filters
filtered = df[
    df["match_source"].isin(selected_matches)
].copy()

if selected_status != "All":
    filtered = filtered[
        filtered["deadline_review_status"]
        == selected_status
    ]

if search:
    found = (
        filtered["title"].str.contains(
            search, case=False, regex=False
        )
        | filtered["buyer"].str.contains(
            search, case=False, regex=False
        )
        | filtered["notice_number"].str.contains(
            search, case=False, regex=False
        )
    )

    filtered = filtered[found]

# Summary cards
col1, col2, col3 = st.columns(3)

col1.metric(
    "All IT tender candidates",
    len(df)
)

col2.metric(
    "Priority review candidates",
    priority_count
)

col3.metric(
    "Matching current filters",
    len(filtered)
)

st.divider()
st.subheader("Tender Intelligence Analytics")

# Display charts using the currently filtered tenders
if filtered.empty:
    st.info("No tenders match the selected filters.")

else:
    chart1 = st.container()
    chart2 = st.container()

    # Chart 1: IT matching methods
    with chart1:
        st.markdown("#### IT Matching Methods")

        method_counts = (
            filtered["match_source"]
            .value_counts()
        )

        st.bar_chart(
            method_counts,
            horizontal=True,
            height=250
            )

    # Chart 2: Deadline review status
    with chart2:
        st.markdown("#### Deadline Review Status")

        deadline_counts = (
            filtered["deadline_review_status"]
            .value_counts()
        )

        st.bar_chart(
            deadline_counts,
            horizontal=True,
            height=300
            )

    # Chart 3: CPV classification statistics
    st.markdown("#### IT CPV Classification")

    cpv_data = filtered[
        ["notice_number", "matching_it_cpv_codes"]
    ].copy()

    cpv_data["cpv_code"] = (
        cpv_data["matching_it_cpv_codes"].str.split(",")
    )

    cpv_data = cpv_data.explode("cpv_code")

    cpv_data["cpv_code"] = (
        cpv_data["cpv_code"].fillna("").str.strip()
    )

    cpv_data = cpv_data[
        cpv_data["cpv_code"].str.fullmatch(
            r"[0-9]{8}", na=False
        )
    ].copy()

    cpv_data["division"] = (
        cpv_data["cpv_code"].str[:2].map({
            "48": "Software packages (48)",
            "72": "IT services (72)"
        })
    )

    cpv_data = (
        cpv_data.dropna(subset=["division"])
        .drop_duplicates(["notice_number", "division"])
    )

    if cpv_data.empty:
        st.info("No matching IT CPV codes in this selection.")
    else:
        cpv_counts = (
            cpv_data["division"].value_counts()
        )

        st.bar_chart(
            cpv_counts,
            horizontal=True,
            height=230
            )

        st.caption(
            "Counts represent distinct tender notices per CPV "
            "division. A notice can appear in both divisions."
        )

st.divider()
st.subheader("IT Tender Opportunities")

# Display the most useful fields
display_columns = [
    "notice_number",
    "title",
    "buyer",
    "match_source",
    "matching_it_cpv_codes",
    "candidate_deadline_date",
    "deadline_review_status",
    "ted_link"
]

st.dataframe(
    filtered[display_columns],
    width="stretch",
    hide_index=True,
    column_config={
        "ted_link": st.column_config.LinkColumn(
            "TED source",
            display_text="View notice"
        )
    }
)

# Download filtered results
st.download_button(
    label="Download filtered report",
    data=filtered.to_csv(
        index=False
    ).encode("utf-8-sig"),
    file_name="filtered_it_tenders.csv",
    mime="text/csv"
)

st.caption(
    "Data source: European Union TED. "
    "This dashboard presents candidates for review."
)
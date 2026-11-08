-- Phase 4: Review tender submission deadlines

WITH source_data AS (

    SELECT
        notice_number,
        deadline_dates,
        deadline_times

    FROM {{ ref('stg_tender_enrichment') }}

),

extracted AS (

    SELECT
        notice_number,

        COALESCE(
            json_array_length(deadline_dates), 0
        ) AS date_count,

        COALESCE(
            json_array_length(deadline_times), 0
        ) AS time_count,

        json_extract_string(
            deadline_dates, '$[0]'
        ) AS first_date_raw,

        json_extract_string(
            deadline_times, '$[0]'
        ) AS first_time_raw

    FROM source_data

),

processed AS (

    SELECT
        notice_number,
        date_count,
        time_count,

        CASE
            WHEN date_count = 1
             AND time_count <= 1
            THEN TRY_CAST(
                LEFT(first_date_raw, 10) AS DATE
            )
            ELSE NULL
        END AS candidate_deadline_date,

        CASE
            WHEN date_count = 1
             AND time_count = 1
            THEN first_time_raw
            ELSE NULL
        END AS candidate_deadline_time

    FROM extracted

)

SELECT
    notice_number,
    candidate_deadline_date,
    candidate_deadline_time,
    date_count,
    time_count,

    CASE
        WHEN date_count = 0
        THEN 'No deadline date reported'

        WHEN date_count > 1 OR time_count > 1
        THEN 'Multiple values - review lots'

        WHEN candidate_deadline_date IS NULL
        THEN 'Invalid date - review'

        WHEN time_count = 0
        THEN 'Date only - review notice'

        ELSE 'Single date/time - verify notice'

    END AS deadline_review_status

FROM processed
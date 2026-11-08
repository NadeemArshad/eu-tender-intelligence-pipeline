-- Validate candidate deadline selection rules

SELECT
    notice_number,
    date_count,
    time_count

FROM {{ ref('int_tender_deadline_review') }}

WHERE
    (
        candidate_deadline_date IS NOT NULL
        AND NOT (
            date_count = 1
            AND time_count <= 1
        )
    )

    OR

    (
        candidate_deadline_time IS NOT NULL
        AND NOT (
            date_count = 1
            AND time_count = 1
        )
    )
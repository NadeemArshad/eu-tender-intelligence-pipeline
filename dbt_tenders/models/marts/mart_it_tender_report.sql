-- Phase 4: Final IT Tender Intelligence Report

WITH opportunities AS (

    SELECT *
    FROM {{ ref('mart_it_opportunities_v2') }}

),

combined AS (

    SELECT
        o.notice_number,

        TRY_CAST(
            LEFT(o.publication_date, 10) AS DATE
        ) AS published_on,

        o.title,
        o.buyer,
        o.country,

        o.match_source,
        o.matching_it_cpv_codes,

        d.candidate_deadline_date,
        d.candidate_deadline_time,

        COALESCE(
            d.date_count, 0
        ) AS reported_date_count,

        COALESCE(
            d.time_count, 0
        ) AS reported_time_count,

        COALESCE(
            d.deadline_review_status,
            'Enrichment unavailable'
        ) AS deadline_review_status,

        CASE
            WHEN d.candidate_deadline_date IS NULL
            THEN 'Deadline unknown - verify TED'

            WHEN d.candidate_deadline_date < CURRENT_DATE
            THEN 'Candidate date passed - verify TED'

            WHEN d.candidate_deadline_date = CURRENT_DATE
            THEN 'Candidate deadline today - verify TED'

            ELSE 'Future candidate date - verify TED'

        END AS opportunity_review_status,

        CASE
            WHEN d.candidate_deadline_date IS NOT NULL
            THEN DATE_DIFF(
                'day',
                CURRENT_DATE,
                d.candidate_deadline_date
            )
            ELSE NULL
        END AS days_until_candidate_deadline,

        o.link AS ted_link

    FROM opportunities AS o

    LEFT JOIN {{ ref('int_tender_deadline_review') }} AS d
        ON o.notice_number = d.notice_number

)

SELECT *
FROM combined

ORDER BY
    CASE
        WHEN opportunity_review_status =
            'Candidate deadline today - verify TED'
        THEN 1

        WHEN opportunity_review_status =
            'Future candidate date - verify TED'
        THEN 2

        WHEN opportunity_review_status =
            'Deadline unknown - verify TED'
        THEN 3

        ELSE 4
    END,

    candidate_deadline_date ASC NULLS LAST,
    published_on DESC NULLS LAST,
    notice_number
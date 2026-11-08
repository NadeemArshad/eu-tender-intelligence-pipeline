-- Phase 4: IT opportunities using CPV and title matching

WITH it_cpv AS (

    SELECT
        notice_number,

        STRING_AGG(
            cpv_code,
            ', ' ORDER BY cpv_code
        ) AS matching_it_cpv_codes

    FROM {{ ref('int_tender_cpv_codes') }}

    WHERE LEFT(cpv_code, 2) IN ('48', '72')

    GROUP BY notice_number

),

combined AS (

    SELECT
        t.notice_number,
        t.publication_date,
        t.title,
        t.buyer,
        t.country,
        t.link,

        t.opportunity_category,
        c.matching_it_cpv_codes,

        t.deadline_dates,
        t.deadline_times,

        CASE
            WHEN c.notice_number IS NOT NULL
             AND t.opportunity_category = 'IT & Digital'
            THEN 'CPV and title'

            WHEN c.notice_number IS NOT NULL
            THEN 'CPV only'

            ELSE 'Title only'
        END AS match_source

    FROM {{ ref('int_tenders_enriched') }} AS t

    LEFT JOIN it_cpv AS c
        ON t.notice_number = c.notice_number

    WHERE
        c.notice_number IS NOT NULL
        OR t.opportunity_category = 'IT & Digital'

)

SELECT *
FROM combined

ORDER BY publication_date DESC, notice_number DESC
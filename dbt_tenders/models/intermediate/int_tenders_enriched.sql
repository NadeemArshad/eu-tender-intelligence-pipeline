-- Join tenders with CPV codes and deadlines

SELECT
    t.notice_number,
    t.publication_date,
    t.title,
    t.buyer,
    t.country,
    t.opportunity_category,
    t.link,

    e.cpv_codes,
    e.deadline_dates,
    e.deadline_times,

    COALESCE(
        json_array_length(e.cpv_codes), 0
    ) AS cpv_code_count,

    COALESCE(
        json_array_length(e.deadline_dates), 0
    ) > 0 AS has_deadline

FROM {{ ref('int_tender_opportunities') }} AS t

LEFT JOIN {{ ref('stg_tender_enrichment') }} AS e
    ON t.notice_number = e.notice_number
-- Inspect tenders not yet categorized

SELECT
    notice_number,
    LEFT(title, 90) AS short_title

FROM {{ ref('int_tender_opportunities') }}

WHERE opportunity_category = 'Other'

ORDER BY notice_number
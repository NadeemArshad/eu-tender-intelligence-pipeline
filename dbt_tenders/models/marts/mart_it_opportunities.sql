-- IT and Digital Tender Opportunities
-- Business-ready dataset for potential IT clients

SELECT
    notice_number,
    publication_date,
    title,
    buyer,
    country,
    notice_type,
    opportunity_category,
    link

FROM {{ ref('int_tender_opportunities') }}

WHERE opportunity_category = 'IT & Digital'

ORDER BY
    publication_date DESC,
    notice_number DESC
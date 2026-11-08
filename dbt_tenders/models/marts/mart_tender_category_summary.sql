-- Step 6: Count tender opportunities by category

SELECT
    opportunity_category,
    COUNT(*) AS total_tenders,
    COUNT(DISTINCT buyer) AS total_buyers

FROM {{ ref('int_tender_opportunities') }}

GROUP BY
    opportunity_category

ORDER BY
    total_tenders DESC
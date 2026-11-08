-- Check that all staging tenders are represented
-- in our category summary.

WITH staging_count AS (

    SELECT COUNT(*) AS total
    FROM {{ ref('stg_tenders') }}

),

mart_count AS (

    SELECT SUM(total_tenders) AS total
    FROM {{ ref('mart_tender_category_summary') }}

)

SELECT
    staging_count.total AS staging_total,
    mart_count.total AS mart_total

FROM staging_count
CROSS JOIN mart_count

WHERE staging_count.total
      IS DISTINCT FROM mart_count.total
-- Phase 3: Our first dbt staging model

SELECT
    notice_number,
    publication_date,
    TRIM(title) AS title,
    TRIM(buyer) AS buyer,
    TRIM(country) AS country,
    notice_type,
    link

FROM {{ source('ted', 'tender_notices') }}
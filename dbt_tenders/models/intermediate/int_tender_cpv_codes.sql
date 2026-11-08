-- Convert CPV JSON arrays into individual rows

WITH extracted AS (

    SELECT
        e.notice_number,
        json_extract_string(j.value, '$') AS cpv_code

    FROM {{ ref('stg_tender_enrichment') }} AS e,
         json_each(e.cpv_codes) AS j

)

SELECT DISTINCT
    notice_number,
    cpv_code

FROM extracted

WHERE regexp_full_match(cpv_code, '^[0-9]{8}$')
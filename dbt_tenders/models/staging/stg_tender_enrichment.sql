-- Phase 4: Staging model for CPV codes and deadlines

SELECT
    notice_number,

    TRY_CAST(cpv_codes_json AS JSON)
        AS cpv_codes,

    TRY_CAST(deadline_dates_json AS JSON)
        AS deadline_dates,

    TRY_CAST(deadline_times_json AS JSON)
        AS deadline_times,

    updated_at

FROM {{ source('ted', 'tender_enrichment') }}
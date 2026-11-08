-- Verify the IT matching categories add up correctly

SELECT *
FROM {{ ref('mart_it_matching_summary') }}

WHERE combined_model_total != (
    additional_cpv_tenders
    + title_only_tenders
    + both_methods_tenders
)

OR keyword_model_total != (
    title_only_tenders
    + both_methods_tenders
)
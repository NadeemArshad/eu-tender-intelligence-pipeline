-- Compare old and new IT opportunity detection

WITH old_model AS (

    SELECT COUNT(*) AS old_total
    FROM {{ ref('mart_it_opportunities') }}

),

new_model AS (

    SELECT
        COUNT(*) AS new_total,

        COUNT(*) FILTER (
            WHERE match_source = 'CPV only'
        ) AS cpv_only,

        COUNT(*) FILTER (
            WHERE match_source = 'Title only'
        ) AS title_only,

        COUNT(*) FILTER (
            WHERE match_source = 'CPV and title'
        ) AS both_methods

    FROM {{ ref('mart_it_opportunities_v2') }}

)

SELECT
    old_model.old_total AS keyword_model_total,

    new_model.new_total AS combined_model_total,

    new_model.cpv_only AS additional_cpv_tenders,

    new_model.title_only AS title_only_tenders,

    new_model.both_methods AS both_methods_tenders,

    new_model.new_total - old_model.old_total
        AS net_additional_tenders

FROM old_model
CROSS JOIN new_model
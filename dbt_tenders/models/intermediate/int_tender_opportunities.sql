-- Improved EU tender classification

WITH staged AS (

    SELECT
        *,
        LOWER(COALESCE(title, '')) AS title_lower

    FROM {{ ref('stg_tenders') }}

)

SELECT
    notice_number,
    publication_date,
    title,
    buyer,
    country,
    notice_type,
    link,

    CASE

        -- IT and Digital
        WHEN title_lower LIKE '%software%'
          OR title_lower LIKE '%cyber%'
          OR title_lower LIKE '%it services%'
          OR title_lower LIKE '%ict-diensten%'
          OR title_lower LIKE '%cloud%'
        THEN 'IT & Digital'

        -- Security
        WHEN title_lower LIKE '%security services%'
          OR title_lower LIKE '%beveiliging%'
          OR title_lower LIKE '%toegangscontrole%'
        THEN 'Security'

        -- Construction
        WHEN title_lower LIKE '%construction%'
          OR title_lower LIKE '%building%'
          OR title_lower LIKE '%bouw%'
          OR title_lower LIKE '%renovatie%'
          OR title_lower LIKE '%installatiewerk%'
        THEN 'Construction & Building'

        -- Energy
        WHEN title_lower LIKE '%energy%'
          OR title_lower LIKE '%energie%'
          OR title_lower LIKE '%electricity%'
          OR title_lower LIKE '%elektriciteit%'
        THEN 'Energy'

        -- Landscaping
        WHEN title_lower LIKE '%grounds maintenance%'
          OR title_lower LIKE '%groenonderhoud%'
          OR title_lower LIKE '%landscaping%'
        THEN 'Landscaping & Grounds'

        -- Events
        WHEN title_lower LIKE '%event services%'
          OR title_lower LIKE '%evenement%'
        THEN 'Events'

        -- Engineering
        WHEN title_lower LIKE '%engineering services%'
          OR title_lower LIKE '%ingenieursdiensten%'
        THEN 'Engineering'

        -- Vehicles
        WHEN title_lower LIKE '%vehicles%'
          OR title_lower LIKE '%wagenpark%'
          OR title_lower LIKE '%voertuigen%'
        THEN 'Vehicles & Fleet'

        -- Maintenance
        WHEN title_lower LIKE '%repair%'
          OR title_lower LIKE '%maintenance%'
          OR title_lower LIKE '%onderhoud%'
          OR title_lower LIKE '%reparatie%'
        THEN 'Maintenance'

        -- Hygiene
        WHEN title_lower LIKE '%hygiene%'
          OR title_lower LIKE '%hygiëne%'
          OR title_lower LIKE '%sanitaire%'
        THEN 'Hygiene & Facilities'

        ELSE 'Other'

    END AS opportunity_category

FROM staged
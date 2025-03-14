{{
    config(
        materialized='incremental',
        unique_key='prd_id',
        indexes=[{"columns": ['prd_id'], "unique": true}],
        target_schema='silver'
    )
}}

with product_cte as (
    SELECT
        p.prd_id AS product_id,
        REPLACE(SUBSTR(p.prd_key, 1, 5), '-', '_') AS category_id,
        SUBSTR(p.prd_key, 7, LENGTH(p.prd_key)) AS product_key,
        p.prd_nm AS product_name,
        COALESCE(p.prd_cost, 0) AS product_cost,
        CASE UPPER(TRIM(p.prd_line))
            WHEN 'M' THEN 'Mountain'
            WHEN 'R' THEN 'Road'
            WHEN 'S' THEN 'Other sales'
            WHEN 'T' THEN 'Touring'
            ELSE 'n/a'
        END AS product_line,
        CAST(p.prd_start_dt AS DATE) AS start_date,
        CAST(LEAD(p.prd_start_dt) OVER (PARTITION BY p.prd_key ORDER BY p.prd_start_dt) - INTERVAL '1 DAY' AS DATE) AS end_date
    FROM {{ source('row_data', 'crm_prd_info') }} AS p
)
SELECT * FROM product_cte
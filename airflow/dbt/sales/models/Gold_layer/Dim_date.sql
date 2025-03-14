{{
    config(
        materialized='view'
    )
}}

WITH dates AS (
    SELECT order_date AS date_value FROM {{ref("crm_salse_details")}}
    UNION 
    SELECT ship_date FROM {{ref("crm_salse_details")}}
    UNION 
    SELECT due_date FROM {{ref("crm_salse_details")}}
),
date_data AS (
    SELECT  
        DISTINCT CAST(date_value AS DATE) AS date_value,
        MD5(CAST(date_value AS STRING)) AS date_key ,
        EXTRACT(YEAR FROM date_value) AS year,
        EXTRACT(MONTH FROM date_value) AS month,
        EXTRACT(DAY FROM date_value) AS day,
        EXTRACT(QUARTER FROM date_value) AS quarter,
        TO_CHAR(date_value, 'Day') AS day_name,
        TO_CHAR(date_value, 'Month') AS month_name
    FROM dates
)
SELECT * FROM date_data

{{
    config(
        materialized='view'
    )
}}

WITH Fact_sales AS (
    SELECT 
        f.order_number,
        f.product_key,
        f.customer_id,
        o_d.date_key AS order_date_key,
        s_d.date_key AS ship_date_key,
        d_d.date_key AS due_date_key,
        f.sales,
        f.quantity,
        f.price
    FROM {{ref("crm_salse_details") }} AS f
    LEFT JOIN {{ref("Dim_product") }} AS p 
        ON f.product_key = p.product_number 
    LEFT JOIN {{ref("Dim_customer") }} AS c 
        ON f.customer_id = c.customer_id
    LEFT JOIN {{ref("Dim_date") }} AS o_d
        ON f.order_date = o_d.date_value 
    LEFT JOIN {{ref("Dim_date") }} AS s_d
        ON f.ship_date = s_d.date_value 
    LEFT JOIN {{ref("Dim_date") }} AS d_d
        ON f.due_date = d_d.date_value 
)
SELECT * FROM Fact_sales

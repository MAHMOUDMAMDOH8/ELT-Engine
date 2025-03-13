{{
    config(
        materialized='incremental',
        unique_key='sls_ord_num',
        indexes=[{"columns": ['sls_ord_num'], "unique": true}],
        target_schema='silver'
    )
}}

with sales_cte as (
    SELECT 
        sls_ord_num AS order_number,
        sls_prd_key AS product_key,
        sls_cust_id AS Customer_id,
        CASE 
            WHEN sls_order_dt = 0 OR LENGTH(sls_order_dt) != 8 THEN TO_DATE(SLS_SHIP_DT::VARCHAR, 'YYYYMMDD') - INTERVAL '2 DAY'
            ELSE TO_DATE(sls_order_dt::VARCHAR, 'YYYYMMDD') 
        END AS order_date,
        CASE 
            WHEN SLS_SHIP_DT = 0 or length(SLS_SHIP_DT) != 8 then NULL
            ELSE TO_DATE(SLS_SHIP_DT::VARCHAR,'YYYYMMDD')
        end as Ship_date,
        CASE 
            WHEN SLS_DUE_DT = 0 or length(SLS_DUE_DT) != 8 then NULL
            else to_date(SLS_DUE_DT::VARCHAR,'YYYYMMDD')
        end as DUE_Date,
        CASE 
            When sls_sales is null or sls_sales <= 0 or sls_sales != sls_quantity * abs(sls_price) then sls_quantity * abs(sls_price)
            else sls_sales
        end as sales,
        sls_quantity as quantity ,
        CASE 
            when sls_price is null or sls_price <= 0 then sls_sales / nullif(sls_quantity,0) 
            else sls_price
        end as price
    FROM {{ source('row_data', 'crm_sales_details') }} s
)
SELECT * from sales_cte
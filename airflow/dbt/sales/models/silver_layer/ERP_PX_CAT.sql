{{
    config(
        materialized='incremental',
        target_schema='silver'
    )
}}

with category_cte as (
    select  
        id as category_id , 
        cat as category ,
        subcat as sub_category,
        maintenance 
    from  {{ source('row_data', 'erp_px_cat_g1v2') }}
)
select * from category_cte
{{
    config(
        materialized='incremental',
        unique_key='cst_id',
        indexes=[{"columns": ['cst_id'], "unique": true}],
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
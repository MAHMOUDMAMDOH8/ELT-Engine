# ELT-Engine
![Architecture drawio](https://github.com/user-attachments/assets/6a855e20-2781-41d9-a84c-a0044314a2d1)

## Table of Contents 
- [Introduction](#introduction)
- [Approach](#approach)
- [Tech Stack & Tools](#tech-stack--tools)
- [Assumptions](#assumptions)
- [Pipeline Architecture](#pipeline-architecture)
- [DBT Models](#DBT-Models)
- [Airflow DAG Overview](#airflow-dag-overview)
- [Data Warehouse Model](#data-warehouse-model)
- [Data Lineage](#data-lineage)
- [Reporting](#reporting)


## Introduction 
This project designed to ingest and transform data from multiple sources (CRM and ERP systems) into Snowflake. It follows the Medallion Architecture to structure data efficiently for analytics. The pipeline leverages dbt (Data Build Tool) to transform raw data into analytics-ready datasets, ensuring high-quality, governed, and optimized data models for reporting and business intelligence.

## Approach
```mermaid
flowchart LR;
A[CRM]
B[ERP]
C[Staging table orders]
D[Join operation]
F[Orders Fact]
G[Staging table products]

A -- "store 'CRM' in data_src" --> C
B -- "store 'ERP' in data_src" --> C

A -- "store 'CRM' in data_src" --> G
B -- "store 'ERP' in data_src" --> G

G -- "create surrogate key" --> Gs[MD5]

C -- "product_id AND data_src" --> D
Gs -- "product_id AND data_src" --> D

D -- "Replace source foreign keys with new products surrogate keys" --> F;
```

## Tech Stack & Tools
- **DBT (Data Build Tool)**: For building and transforming data models.
- **Snowflake**: As the data warehouse.
- **Docker**: To containerize and standardize the development environment.
- **Python**: For scripting and automation.
- **Airflow** : For orchestrating ETL workflows.
- **Power BI** : For visualizing the reporting layer.

## Assumptions
Snowflake is the database platform used for data storage and transformations.
Docker is installed and used for containerized environments.
Required datasets are accessible in a suitable format (CSV).

## Pipeline Architecture 
![Medallion Architecture drawio](https://github.com/user-attachments/assets/16d30a2f-3108-4fef-9735-ae712475366f)

The project follows the Medallion Architecture, which organizes data into three layers:

    Bronze Layer (Raw Data): Stores unprocessed and ingested data from various sources.
    Silver Layer (Cleansed Data): Cleans and pre-processes data for transformation and enrichment.
    Gold Layer (Aggregated Data): Optimized for analytics, reporting, and business intelligence.

## Airflow DAG Overview
![Screenshot from 2025-03-15 04-30-57](https://github.com/user-attachments/assets/2917450e-6dde-4aee-9cc5-0a897597b5b4)

![Screenshot from 2025-03-15 04-29-31](https://github.com/user-attachments/assets/df7a98a4-3186-4051-841e-5a84f43dcc0e)

If using Airflow for orchestration, the DAG performs the following tasks:

Extract: Reads raw data from (CRM and ERP systems) .
Load: Loads data into the Snowflake .
Transform: Executes DBT models to build Bronze Layer (Raw Data),Silver Layer (Cleansed Data) , and Gold Layer (Aggregated Data) .
see more : [airflow DAG](https://github.com/MAHMOUDMAMDOH8/ELT-Engine/blob/main/airflow/dags/pipeline.py)


## DBT Models
#### customer_cte
 
    {{
    config(
        materialized='incremental',
        unique_key='ID',
        indexes=[{"columns": ['ID'], "unique": true}],
        target_schema='silver'
    )
    }}
    
    with customer_cte as (
        SELECT 
            *, 
            row_number() OVER (PARTITION BY cst_id ORDER BY cst_create_date DESC) AS last_update
        FROM {{ source('row_data', 'crm_cust_info') }}
    )
    
    SELECT 
        cst_id AS ID,
        cst_key AS customer_key, 
        TRIM(cst_firstname) AS FIRST_NAME, 
        TRIM(cst_lastname) AS LAST_NAME,
        CASE 
            WHEN UPPER(cst_marital_status) = 'S' THEN 'Single'
            WHEN UPPER(cst_marital_status) = 'M' THEN 'Married'
            ELSE 'n/a'
        END AS MARITAL_STATUS,
        CASE 
            WHEN UPPER(cst_gndr) = 'F' THEN 'Female'
            WHEN UPPER(cst_gndr) = 'M' THEN 'Male'
            ELSE 'n/a'
        END AS gender,
        cst_create_date 
    FROM customer_cte
    WHERE last_update = 1 and cst_id is not null
#### sales_cte

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

see more : [DBT Models](https://github.com/MAHMOUDMAMDOH8/ELT-Engine/tree/main/airflow/dbt/sales/models)


## Data Warehouse Model 
```mermaid
erDiagram
    customer_dim {
        string customer_sk
        int customer_id
        string customer_unique_key
        string first_name
        string last_name
        string gender
        date birth_date
        string country
    }

    date_dim {
        string date_key
        date date_value
        int year
        int month
        int day
        int quarter
        string day_name
        string month_name
    }

    product_dim {
        string product_sk
        int product_id
        string product_number
        string product_name
        string category
        string sub_category
        string maintenance
        float product_cost
        string product_line
        date start_date
    }

    sales_fact {
        string order_number
        string product_key
        string customer_id
        string order_date_key
        string ship_date_key
        string due_date_key
        float sales
        int quantity
        float price
    }

    %% Relationships
    sales_fact ||--o{ customer_dim : "belongs to"
    sales_fact ||--o{ product_dim : "contains"
    sales_fact ||--o{ date_dim : "ordered on"
    sales_fact ||--o{ date_dim : "shipped on"
    sales_fact ||--o{ date_dim : "due on"
```

## Data Lineage 
![Lineage Graph](https://github.com/user-attachments/assets/bc59f140-e299-43e0-b3b3-59d5c340003e)

## Reporting
### overview 
![overview](https://github.com/user-attachments/assets/a702dcb2-6db3-4aee-9dce-d704929fa79b)

### customers
![customers](https://github.com/user-attachments/assets/800d429c-6be6-48d4-9bef-fcadfaa637b5)

For any queries, feel free to reach out! 
# Contact Information
📧 Email: [mahmoud.mamdoh0812@gmail.com](mailto:mahmoud.mamdoh0812@gmail.com)  
🔗 LinkedIn: [Mahmoud Mamdoh](https://www.linkedin.com/in/mahmoud-mamdoh-47a68a203/)  
🐦 Twitter: [@M7M0UD_D](https://x.com/M7M0UD_D)

For any queries, feel free to reach out!









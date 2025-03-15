# ELT-Engine
![Architecture drawio](https://github.com/user-attachments/assets/6a855e20-2781-41d9-a84c-a0044314a2d1)

## Table of Contents 
- [Introduction](#introduction)
- [Approach](#approach)
- [Tech Stack & Tools](#tech-stack--tools)
- [Assumptions](#assumptions)
- [Pipeline Architecture](#pipeline-architecture)
- [DBT Directory Structure](#dbt-directory-structure)
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
- **Airflow** (optional): For orchestrating ETL workflows.
- **Power BI** (optional): For visualizing the reporting layer.

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

Extract: Reads raw data from source olap database or APIs.
Load: Loads data into the PostgreSQL database.
Transform: Executes DBT models to build staging, dimension, and fact tables.

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

    -- Relationships
    sales_fact ||--o{ customer_dim : "customer_id"
    sales_fact ||--o{ product_dim : "product_key"
    sales_fact ||--o{ date_dim : "order_date_key"
    sales_fact ||--o{ date_dim : "ship_date_key"
    sales_fact ||--o{ date_dim : "due_date_key"
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









from Scripts.snowflake_utilz import *
from Scripts.ingest_data import *
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from dotenv import load_dotenv


load_dotenv("secrets.env")


default_args = {
    'owner': 'Mahmoud',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}


dag = DAG(
    'sales_pipeline',
    default_args=default_args,
    description='ELT engine',
    schedule_interval='*/15 * * * *',
    start_date=days_ago(1),
    catchup=False
)

crm_path = "/opt/airflow/Source/source_crm"
erp_path = "/opt/airflow/Source/source_erp"

def snowflake_credentials():
    return {
        'user': os.getenv("SNOWFLAKE_USER"),
        'password': os.getenv("SNOWFLAKE_PASSWORD"),
        'account': os.getenv("SNOWFLAKE_ACCOUNT"),
        'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE"),
        'database': os.getenv("SNOWFLAKE_DATABASE"),
        'schema': os.getenv("SNOWFLAKE_SCHEMA"),
    }


#  Snowflake connection
def test_snowflake_connection():
    snowflake_cred = snowflake_credentials()
    conn, engine = snowFlaek_connection(**snowflake_cred)
    if conn is None or engine is None:
        logging.error("❌ Snowflake connection failed!")
        raise Exception("Snowflake connection could not be established.")
    logging.info("✅ Snowflake connection successful!")
    close_connection(conn, engine)

# PostgreSQL credentials 
def postgres_credentials():
    return {
        'host': os.getenv("POSTGRES_HOST"),
        'db_name': os.getenv("POSTGRES_DB"),
        'user': os.getenv("POSTGRES_USER"),
        'password': os.getenv("POSTGRES_PASSWORD"),
    }


#ingest CRM data
def ingest_crm_data():


    snowflake_cred = snowflake_credentials()
    Snow_conn, Snow_engine = snowFlaek_connection(**snowflake_cred)

    postgres_cred = postgres_credentials()
    Post_conn, Post_engine = postgres_connection(**postgres_cred)


    logging.info("📥 Ingesting CRM data...")


    crm_cus = os.path.join(crm_path, "cust_info.csv")
    ingest_data(crm_cus, "crm_cust_info", Snow_conn, Snow_engine, Post_conn)

    crm_pro = os.path.join(crm_path, "prd_info.csv")
    ingest_data(crm_pro, "crm_prd_info", Snow_conn, Snow_engine, Post_conn)

    crm_sales = os.path.join(crm_path, "sales_details.csv")
    ingest_data(crm_sales, "crm_sales_details", Snow_conn, Snow_engine, Post_conn)

    close_connection(Snow_conn, Snow_engine)
    close_connection(Post_conn, Post_engine)


# ingest ERP data
def ingest_erp_data():

    logging.info(crm_path)

    snowflake_cred = snowflake_credentials()
    Snow_conn, Snow_engine = snowFlaek_connection(**snowflake_cred)

    postgres_cred = postgres_credentials()
    Post_conn, Post_engine = postgres_connection(**postgres_cred)
    
    logging.info("📥 Ingesting ERP data...")

    erp_cus = os.path.join(erp_path, "CUST_AZ12.csv")
    ingest_data(erp_cus, "erp_cust_az12", Snow_conn, Snow_engine, Post_conn)

    erp_loc = os.path.join(erp_path, "LOC_A101.csv")
    ingest_data(erp_loc, "erp_loc_a101", Snow_conn, Snow_engine, Post_conn)

    erp_px = os.path.join(erp_path, "PX_CAT_G1V2.csv")
    ingest_data(erp_px, "erp_px_cat_g1v2", Snow_conn, Snow_engine, Post_conn)

    close_connection(Snow_conn, Snow_engine)
    close_connection(Post_conn, Post_engine)


with dag:
    test_connection_task = PythonOperator(
        task_id='test_snowflake_connection',
        python_callable=test_snowflake_connection
    )

    ingest_crm_data_task = PythonOperator(
        task_id='ingest_crm_data',
        python_callable=ingest_crm_data
    )

    ingest_erp_data_task = PythonOperator(
        task_id='ingest_erp_data',
        python_callable=ingest_erp_data
    )

    test_connection_task >> [ingest_crm_data_task, ingest_erp_data_task]
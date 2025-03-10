from Scripts.snowflake_utilz import *
import pandas as pd
import os
import logging

def ingest_data(path, table_name, snow_connection, snow_engine,post_connn):
    try:
        file_name = os.path.basename(path)

        # Check if the file is  processed
        if is_file_processed(post_connn, file_name):
            logging.info(f"File {file_name} has already been processed. Skipping ingestion.")
            return 
        
        logging.info(f"Start ingesting {file_name} into {table_name}")

        df = pd.read_csv(path)

        # Insert data into Snowflake
        insert_raw_data(table_name, df, snow_connection, snow_engine)


        mark_file_as_processed(post_connn, file_name)

        logging.info(f"Data ingested successfully into {table_name}")

    except Exception as e:
        logging.error(f"Error ingesting data from {file_name} into {table_name}: {e}")


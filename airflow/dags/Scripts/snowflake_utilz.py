from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

def snowFlaek_connection(user, password, account, warehouse, database, schema):

    Conn_str = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}"

    try:
        engine = create_engine(Conn_str)
        connection = engine.connect()
        logging.info("Connected to snowflake successfully")
        return connection,engine
    except SQLAlchemyError as e :
        logging.info(f"error while connecting to snowflake : {e}")
        return None,None

def postgres_connection(host, db_name, user, password):

    connection_string = f'postgresql://{user}:{password}@{host}/{db_name}'

    try:
        engine = create_engine(connection_string)
        connection = engine.connect()
        logging.info("Connected to PostgreSQL database successfully")
        return connection, engine
    except SQLAlchemyError as error:
        logging.error("Error while connecting to PostgreSQL: %s", error)
        return None, None
    
def close_connection(connection, engine):
    if connection:
        connection.close()
        logging.info("connection is closed")
    if engine:
        engine.dispose()
        logging.info("SQLAlchemy engine disposed")


def insert_raw_data(table_name,data_frame,connection,engine):
    logging.info(f"loading raw data into table {table_name}")

    if connection:
        try:
            data_frame.to_sql(name=table_name, con=engine, if_exists='append', index=False)
            logging.info(f"raw data loaded successfully into {table_name} with {len(data_frame)} rows")
        except SQLAlchemyError as e:
            logging.info(f"error while load raw data : {e} ")
    else:
        logging.info(f"Failed to connect to the database and load data into table {table_name}")



def is_file_processed(conn, file_name):
    query = text("SELECT 1 FROM processed_files WHERE file_name = :file_name")
    result = conn.execute(query, {'file_name': file_name}).fetchone()
    return result is not None

def mark_file_as_processed(conn, file_name):
    query = text("INSERT INTO processed_files (file_name) VALUES (:file_name)")
    conn.execute(query, {'file_name': file_name})
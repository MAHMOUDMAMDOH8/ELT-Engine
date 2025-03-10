FROM apache/airflow:2.9.0

RUN pip install --upgrade pip \
	&& pip install markupsafe \
	&& pip install apache-airflow-providers-postgres \
	&& pip install apache-airflow-providers-odbc \
	&& pip install psycopg2-binary \
	&& pip install gitpython \
	&& pip install dbt-airflow \
	&& pip install plyvel \
	&& pip install --upgrade cmake \
	&& pip install --upgrade pyarrow \
	&& pip install apache-airflow-providers-trino \
	&& pip install dbt-snowflake \
	&& pip install dbt-core


USER root
RUN sudo apt-get update
RUN sudo apt-get install -y git

USER airflow
RUN airflow db migrate

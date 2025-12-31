import os
import pandas as pd
import yaml
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

DATASET_DIR = "/opt/airflow/airflow-dags/extraction/email_thread_details"
CSV_FILE = f"{DATASET_DIR}/sample_data/email_thread_details.csv"
TRANSFORMED_FILE = f"{DATASET_DIR}/sample_data/transformed.csv"
SCHEMA_FILE = f"{DATASET_DIR}/config/schema_expected.yaml"
DDL_FILE = f"{DATASET_DIR}/config/create_table.sql"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
}

def check_file_exists():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"CSV file not found at {CSV_FILE}")

def validate_schema():
    with open(SCHEMA_FILE, "r") as f:
        schema = yaml.safe_load(f)

    expected_columns = [c["name"] for c in schema["columns"]]
    non_nullable = [c["name"] for c in schema["columns"] if not c.get("nullable", True)]

    df = pd.read_csv(CSV_FILE)

    if set(expected_columns) != set(df.columns):
        raise ValueError("CSV columns do not match schema")

    for col in non_nullable:
        if df[col].isnull().any():
            raise ValueError(f"Non-nullable column has NULLs: {col}")

def transform_data():
    df = pd.read_csv(CSV_FILE)

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df.replace("", pd.NA, inplace=True)

    if "status" in df.columns:
        df = df[df["status"].str.lower() != "done"]

    df.to_csv(TRANSFORMED_FILE, index=False)

def load_to_postgres():
    df = pd.read_csv(TRANSFORMED_FILE)

    conn = psycopg2.connect(
        host=os.environ["PG_HOST"],
        port=os.environ["PG_PORT"],
        dbname=os.environ["PG_DB"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
    )

    cur = conn.cursor()

    with open(DDL_FILE, "r") as f:
        cur.execute(f.read())

    cols = list(df.columns)
    placeholders = ",".join(["%s"] * len(cols))
    quoted_cols = [f'"{c}"' for c in cols]

    insert_sql = f"""
        INSERT INTO public.email_thread_details ({','.join(quoted_cols)})
        VALUES ({placeholders})
    """

    for row in df.itertuples(index=False, name=None):
        cur.execute(insert_sql, row)

    conn.commit()
    cur.close()
    conn.close()

with DAG(
    dag_id="email_thread_details_ingest",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["extraction", "email_thread_details"],
) as dag:

    file_check = PythonOperator(
        task_id="check_file_exists",
        python_callable=check_file_exists,
    )

    schema_validation = PythonOperator(
        task_id="validate_schema",
        python_callable=validate_schema,
    )

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres,
    )

    file_check >> schema_validation >> transform >> load

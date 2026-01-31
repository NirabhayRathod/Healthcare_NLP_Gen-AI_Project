from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from src.Text_preprocessing import run_preprocessing

with DAG(
    dag_id="drug_review_preprocessing",
    start_date=datetime(2024, 2, 1),
    schedule="@weekly",
    catchup=False,
    default_args={
        "owner": "mlops",
        "retries": 1,
    },
    tags=["healthcare", "nlp", "preprocessing"],
) as dag:

    @task
    def preprocess_task():
        """
        Executes full preprocessing pipeline:
        raw_data -> preprocessing -> processed_data
        """
        return run_preprocessing()

    preprocess_task()

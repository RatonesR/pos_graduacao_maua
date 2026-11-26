from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    "owner": "engenharia_dados",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="ecommerce_lakehouse_ai_pipeline",
    default_args=default_args,
    description="Pipeline End-to-End: Ingestão Bronze Iceberg -> dbt Silver/Gold -> ML & RAG",
    schedule="@daily",
    start_date=datetime(2026, 11, 1),
    catchup=False,
    tags=["lakehouse", "iceberg", "dbt", "ia"],
) as dag:

    common_kwargs = {
        "cwd": "/opt/airflow",
    }

    setup_minio = BashOperator(
        task_id="setup_minio_buckets",
        bash_command="python /opt/airflow/scripts/1_setup_minio.py",
        **common_kwargs,
    )

    ingest_cdc = BashOperator(
        task_id="ingest_bronze_relacional_cdc",
        bash_command="python /opt/airflow/scripts/2_ingest_relacional_cdc.py",
        **common_kwargs,
    )

    ingest_clickstream = BashOperator(
        task_id="ingest_bronze_clickstream",
        bash_command="python /opt/airflow/scripts/3_ingest_stream_clickstream.py",
        **common_kwargs,
    )

    ingest_iot = BashOperator(
        task_id="ingest_bronze_iot_telemetria",
        bash_command="python /opt/airflow/scripts/4_ingest_iot_telemetria.py",
        **common_kwargs,
    )

    ingest_textos = BashOperator(
        task_id="ingest_bronze_textos_reviews",
        bash_command="python /opt/airflow/scripts/5_ingest_textos_reviews.py",
        **common_kwargs,
    )

    dbt_run = BashOperator(
        task_id="dbt_run_silver_gold",
        bash_command="/opt/airflow/dbt_venv/bin/dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project",
        **common_kwargs,
    )

    dbt_test = BashOperator(
        task_id="dbt_test_qualidade",
        bash_command="/opt/airflow/dbt_venv/bin/dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project",
        **common_kwargs,
    )

    export_s3 = BashOperator(
        task_id="export_silver_gold_minio",
        bash_command="/opt/airflow/dbt_venv/bin/python /opt/airflow/scripts/6_export_gold_to_minio.py",
        **common_kwargs,
    )

    run_ia = BashOperator(
        task_id="consumo_ia_churn_e_rag",
        bash_command="python /opt/airflow/scripts/7_ia_consumo_churn_e_rag.py",
        **common_kwargs,
    )

    setup_minio >> [ingest_cdc, ingest_clickstream, ingest_iot, ingest_textos] >> dbt_run >> dbt_test >> export_s3 >> run_ia
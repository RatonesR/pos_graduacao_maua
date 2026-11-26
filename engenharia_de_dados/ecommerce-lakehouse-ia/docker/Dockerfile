FROM docker-airflow-init:latest

RUN pip uninstall -y astronomer-cosmos && \
    /opt/airflow/dbt_venv/bin/pip install --no-cache-dir astronomer-cosmos==1.11.0
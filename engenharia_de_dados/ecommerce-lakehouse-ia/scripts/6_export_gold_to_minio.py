import os
import duckdb


def exportar_camadas_para_s3() -> None:
    con = duckdb.connect("/opt/airflow/data/lakehouse.duckdb", read_only=True)
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(
        f"""
        SET s3_endpoint='{os.getenv("MINIO_ENDPOINT_HOST", "minio:9000")}';
        SET s3_access_key_id='{os.getenv("MINIO_ROOT_USER", "lakehouse_admin")}';
        SET s3_secret_access_key='{os.getenv("MINIO_ROOT_PASSWORD", "lakehouse_secret_2026")}';
        SET s3_region='us-east-1';
        SET s3_url_style='path';
        SET s3_use_ssl=false;
        """
    )

    tabelas_silver = [
        "slv_clientes",
        "slv_pedidos",
        "slv_clickstream_telemetria",
        "slv_documentos_nlp",
    ]
    for tabela in tabelas_silver:
        destino = f"s3://silver/{tabela}/dados.parquet"
        con.execute(f"COPY main_silver.{tabela} TO '{destino}' (FORMAT PARQUET);")
        print(f"[SILVER S3 OK] {destino}")

    tabelas_gold = [
        "gold_feature_store_churn",
        "gold_rag_base_conhecimento",
    ]
    for tabela in tabelas_gold:
        destino = f"s3://gold/{tabela}/dados.parquet"
        con.execute(f"COPY main_gold.{tabela} TO '{destino}' (FORMAT PARQUET);")
        print(f"[GOLD S3 OK] {destino}")

    con.close()


if __name__ == "__main__":
    exportar_camadas_para_s3()
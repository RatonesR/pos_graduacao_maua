import os
from datetime import datetime, timezone
import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, NoSuchTableError
from pyiceberg.transforms import DayTransform


def obter_catalogo_iceberg() -> SqlCatalog:
    """Inicializa o catálogo Apache Iceberg apontando para o MinIO (S3)."""
    os.makedirs("/opt/airflow/data", exist_ok=True)
    return SqlCatalog(
        "ecommerce_lakehouse",
        **{
            "uri": "sqlite:////opt/airflow/data/iceberg_catalog.db",
            "warehouse": "s3://bronze",
            "s3.endpoint": os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
            "s3.access-key-id": os.getenv("MINIO_ROOT_USER", "lakehouse_admin"),
            "s3.secret-access-key": os.getenv("MINIO_ROOT_PASSWORD", "lakehouse_secret_2026"),
            "s3.region": "us-east-1",
            "s3.path-style-access": "true",
        },
    )


def gravar_tabela_bronze(
    df: pd.DataFrame,
    nome_tabela: str,
    fonte_sistema: str,
    versao_schema: str = "1.0",
) -> str:
    """Adiciona metadados técnicos e realiza escrita append-only ACID no Iceberg."""
    df_enriquecido = df.copy()
    agora_utc = datetime.now(timezone.utc)

    df_enriquecido["_ingerido_em"] = agora_utc
    df_enriquecido["_fonte_sistema"] = fonte_sistema
    df_enriquecido["_versao_schema"] = versao_schema

    tabela_arrow = pa.Table.from_pandas(df_enriquecido, preserve_index=False)
    catalogo = obter_catalogo_iceberg()

    try:
        catalogo.create_namespace("bronze")
    except NamespaceAlreadyExistsError:
        pass

    identificador = f"bronze.{nome_tabela}"

    try:
        tabela = catalogo.load_table(identificador)
    except NoSuchTableError:
        tabela = catalogo.create_table(
            identifier=identificador,
            schema=tabela_arrow.schema,
        )
        with tabela.update_spec() as spec:
            spec.add_field("_ingerido_em", DayTransform(), "dia_ingestao")

    tabela.append(tabela_arrow)
    snapshot_atual = tabela.current_snapshot().snapshot_id
    print(f"[BRONZE OK] {identificador} | {len(df_enriquecido)} registros | snapshot_id={snapshot_atual}")
    return str(snapshot_atual)
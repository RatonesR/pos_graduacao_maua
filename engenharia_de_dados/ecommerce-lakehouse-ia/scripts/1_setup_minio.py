import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


def criar_buckets_medallion() -> None:
    """Inicializa os buckets S3 no MinIO para a Arquitetura Medallion e Iceberg."""
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ROOT_USER", "lakehouse_admin")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", "lakehouse_secret_2026")

    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    buckets = ["bronze", "silver", "gold", "warehouse"]

    for bucket in buckets:
        try:
            s3_client.head_bucket(Bucket=bucket)
            print(f"[OK] Bucket '{bucket}' já existe.")
        except ClientError:
            s3_client.create_bucket(Bucket=bucket)
            print(f"[CRIADO] Bucket '{bucket}' inicializado com sucesso.")


if __name__ == "__main__":
    criar_buckets_medallion()
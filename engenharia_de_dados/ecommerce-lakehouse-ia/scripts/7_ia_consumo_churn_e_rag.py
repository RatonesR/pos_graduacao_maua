import os
import pandas as pd
import pyarrow.fs as fs
import pyarrow.parquet as pq
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def obter_s3_fs() -> fs.S3FileSystem:
    return fs.S3FileSystem(
        endpoint_override=os.getenv("MINIO_ENDPOINT_HOST", "minio:9000"),
        access_key=os.getenv("MINIO_ROOT_USER", "lakehouse_admin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "lakehouse_secret_2026"),
        scheme="http",
        region="us-east-1",
    )


def executar_pipeline_ia() -> None:
    s3 = obter_s3_fs()

    # 1. Consumo Tabular: Feature Store Gold -> Predição de Risco de Churn
    df_features = pq.read_table("gold/gold_feature_store_churn/dados.parquet", filesystem=s3).to_pandas()
    print("\n=== [IA - FEATURE STORE GOLD] ===")
    print(df_features[["cliente_id", "segmento", "receita_total_brl", "total_abandonos_carrinho", "nota_media_avaliacao", "flag_risco_churn"]])

    colunas_x = [
        "qtd_pedidos",
        "receita_total_brl",
        "ticket_medio_brl",
        "total_sessoes",
        "total_abandonos_carrinho",
        "tempo_medio_navegacao_seg",
        "nota_media_avaliacao",
    ]
    X = df_features[colunas_x]
    y = df_features["flag_risco_churn"]

    modelo_churn = RandomForestClassifier(n_estimators=50, random_state=42)
    modelo_churn.fit(X, y)
    df_features["probabilidade_churn"] = modelo_churn.predict_proba(X)[:, 1].round(3)

    print("\n=== [IA - SCORING DE CHURN] ===")
    print(df_features[["cliente_id", "flag_risco_churn", "probabilidade_churn"]])

    # 2. Consumo Generativo / RAG: Base de Conhecimento Gold (Dados Sanitizados LGPD)
    df_rag = pq.read_table("gold/gold_rag_base_conhecimento/dados.parquet", filesystem=s3).to_pandas()
    print("\n=== [IA - BASE RAG SANITIZADA (SEM PII)] ===")
    for _, row in df_rag.iterrows():
        print(f"- [{row['documento_id']} | {row['tipo_documento']}]: {row['conteudo_contextualizado']}")

    # Recuperação Semântica (Retrieval) sobre a camada Gold
    consulta_usuario = "Qual o prazo de devolução e cancelamento?"
    vetorizador = TfidfVectorizer()
    matriz_docs = vetorizador.fit_transform(df_rag["conteudo_contextualizado"])
    vetor_query = vetorizador.transform([consulta_usuario])

    similaridades = cosine_similarity(vetor_query, matriz_docs).flatten()
    idx_top = similaridades.argmax()
    doc_recuperado = df_rag.iloc[idx_top]

    print("\n=== [IA - RECUPERAÇÃO RAG] ===")
    print(f"Pergunta: '{consulta_usuario}'")
    print(f"Documento Recuperado ({doc_recuperado['documento_id']}, score={similaridades[idx_top]:.3f}):")
    print(f"Contexto Seguro Enviado ao LLM: {doc_recuperado['conteudo_contextualizado']}")


if __name__ == "__main__":
    executar_pipeline_ia()
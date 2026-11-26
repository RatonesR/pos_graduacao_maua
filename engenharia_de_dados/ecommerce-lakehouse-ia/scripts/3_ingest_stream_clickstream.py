import pandas as pd
import pandera as pa
from pandera import Column, Check
from bronze_writer import gravar_tabela_bronze


SCHEMA_CLICKSTREAM = pa.DataFrameSchema(
    {
        "evento_id": Column(str, nullable=False),
        "sessao_id": Column(str, nullable=False),
        "cliente_id": Column(str, nullable=True),
        "tipo_evento": Column(str, Check.isin(["page_view", "search", "add_to_cart", "checkout_abandon", "purchase"]), nullable=False),
        "dispositivo": Column(str, Check.isin(["mobile_ios", "mobile_android", "web_desktop"]), nullable=False),
        "duracao_segundos": Column(int, Check.greater_than_or_equal_to(0), nullable=False),
        "evento_timestamp": Column(str, nullable=False),
    }
)


def executar_ingestao_clickstream() -> None:
    eventos = [
        {"evento_id": "EVT-901", "sessao_id": "SES-01", "cliente_id": "CLI-001", "tipo_evento": "page_view", "dispositivo": "mobile_ios", "duracao_segundos": 45, "evento_timestamp": "2026-11-05T11:50:00Z"},
        {"evento_id": "EVT-902", "sessao_id": "SES-01", "cliente_id": "CLI-001", "tipo_evento": "add_to_cart", "dispositivo": "mobile_ios", "duracao_segundos": 120, "evento_timestamp": "2026-11-05T11:55:00Z"},
        {"evento_id": "EVT-902", "sessao_id": "SES-01", "cliente_id": "CLI-001", "tipo_evento": "add_to_cart", "dispositivo": "mobile_ios", "duracao_segundos": 120, "evento_timestamp": "2026-11-05T11:55:00Z"},
        {"evento_id": "EVT-903", "sessao_id": "SES-02", "cliente_id": "CLI-002", "tipo_evento": "checkout_abandon", "dispositivo": "web_desktop", "duracao_segundos": 310, "evento_timestamp": "2026-11-12T20:10:00Z"},
        {"evento_id": "EVT-904", "sessao_id": "SES-03", "cliente_id": "CLI-004", "tipo_evento": "checkout_abandon", "dispositivo": "mobile_android", "duracao_segundos": 180, "evento_timestamp": "2026-09-01T19:00:00Z"},
    ]

    df_val = SCHEMA_CLICKSTREAM.validate(pd.DataFrame(eventos))
    gravar_tabela_bronze(df_val, "stream_clickstream_eventos", "kafka_clickstream_topic")


if __name__ == "__main__":
    executar_ingestao_clickstream()
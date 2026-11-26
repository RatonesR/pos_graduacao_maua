import pandas as pd
import pandera as pa
from pandera import Column, Check
from bronze_writer import gravar_tabela_bronze


SCHEMA_IOT = pa.DataFrameSchema(
    {
        "leitura_id": Column(str, nullable=False),
        "veiculo_id": Column(str, nullable=False),
        "pedido_id": Column(str, nullable=True),
        "temperatura_celsius": Column(float, nullable=False),
        "vibracao_g": Column(float, Check.greater_than_or_equal_to(0.0), nullable=False),
        "velocidade_kmh": Column(float, Check.greater_than_or_equal_to(0.0), nullable=False),
        "leitura_timestamp": Column(str, nullable=False),
    }
)


def executar_ingestao_iot() -> None:
    telemetria = [
        {"leitura_id": "IOT-01", "veiculo_id": "VAN-10", "pedido_id": "PED-1001", "temperatura_celsius": 4.2, "vibracao_g": 0.12, "velocidade_kmh": 62.5, "leitura_timestamp": "2026-11-06T09:00:00Z"},
        {"leitura_id": "IOT-02", "veiculo_id": "VAN-10", "pedido_id": "PED-1001", "temperatura_celsius": 4.5, "vibracao_g": 0.14, "velocidade_kmh": 58.0, "leitura_timestamp": "2026-11-06T09:15:00Z"},
        {"leitura_id": "IOT-03", "veiculo_id": "VAN-22", "pedido_id": "PED-1003", "temperatura_celsius": 19.8, "vibracao_g": 1.85, "velocidade_kmh": 95.0, "leitura_timestamp": "2026-11-19T14:00:00Z"},
        {"leitura_id": "IOT-04", "veiculo_id": "VAN-22", "pedido_id": "PED-1003", "temperatura_celsius": -999.0, "vibracao_g": 0.10, "velocidade_kmh": 0.0, "leitura_timestamp": "2026-11-19T14:15:00Z"},
    ]

    df_val = SCHEMA_IOT.validate(pd.DataFrame(telemetria))
    gravar_tabela_bronze(df_val, "iot_telemetria_frota", "mqtt_iot_gateway")


if __name__ == "__main__":
    executar_ingestao_iot()
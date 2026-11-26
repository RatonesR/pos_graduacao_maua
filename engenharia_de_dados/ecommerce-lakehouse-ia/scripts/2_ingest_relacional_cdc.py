import pandas as pd
import pandera as pa
from pandera import Column, Check
from bronze_writer import gravar_tabela_bronze


SCHEMA_CLIENTES = pa.DataFrameSchema(
    {
        "cliente_id": Column(str, Check.str_startswith("CLI-"), nullable=False),
        "nome_completo": Column(str, nullable=False),
        "cpf": Column(str, Check.str_length(min_value=11, max_value=14), nullable=False),
        "email": Column(str, Check.str_contains("@"), nullable=False),
        "uf": Column(str, Check.str_length(2, 2), nullable=False),
        "segmento": Column(str, Check.isin(["standard", "plus", "vip"]), nullable=False),
        "op_cdc": Column(str, Check.isin(["I", "U", "D"]), nullable=False),
        "atualizado_em": Column(str, nullable=False),
    }
)

SCHEMA_PEDIDOS = pa.DataFrameSchema(
    {
        "pedido_id": Column(str, Check.str_startswith("PED-"), nullable=False),
        "cliente_id": Column(str, Check.str_startswith("CLI-"), nullable=False),
        "categoria_produto": Column(str, nullable=False),
        "valor_centavos": Column(int, Check.greater_than(0), nullable=False),
        "status_origem": Column(str, nullable=False),
        "criado_em": Column(str, nullable=False),
        "op_cdc": Column(str, Check.isin(["I", "U", "D"]), nullable=False),
    }
)


def executar_ingestao_relacional() -> None:
    df_clientes = pd.DataFrame(
        [
            {"cliente_id": "CLI-001", "nome_completo": "Ana Souza", "cpf": "12345678901", "email": "ana@email.com", "uf": "SP", "segmento": "vip", "op_cdc": "I", "atualizado_em": "2026-11-01T10:00:00Z"},
            {"cliente_id": "CLI-002", "nome_completo": "Bruno Lima", "cpf": "98765432100", "email": "bruno@email.com", "uf": "RJ", "segmento": "standard", "op_cdc": "I", "atualizado_em": "2026-11-02T11:30:00Z"},
            {"cliente_id": "CLI-002", "nome_completo": "Bruno Lima", "cpf": "98765432100", "email": "bruno@email.com", "uf": "RJ", "segmento": "plus", "op_cdc": "U", "atualizado_em": "2026-11-15T14:20:00Z"},
            {"cliente_id": "CLI-003", "nome_completo": "Carla Mendes", "cpf": "45678912399", "email": "carla@email.com", "uf": "MG", "segmento": "plus", "op_cdc": "I", "atualizado_em": "2026-11-03T09:15:00Z"},
            {"cliente_id": "CLI-004", "nome_completo": "Diego Rocha", "cpf": "32165498711", "email": "diego@email.com", "uf": "PR", "segmento": "standard", "op_cdc": "I", "atualizado_em": "2026-08-10T16:45:00Z"},
        ]
    )

    df_pedidos = pd.DataFrame(
        [
            {"pedido_id": "PED-1001", "cliente_id": "CLI-001", "categoria_produto": "Eletrônicos", "valor_centavos": 349900, "status_origem": "PAID", "criado_em": "2026-11-05T12:00:00Z", "op_cdc": "I"},
            {"pedido_id": "PED-1001", "cliente_id": "CLI-001", "categoria_produto": "Eletrônicos", "valor_centavos": 349900, "status_origem": "DELIVERED", "criado_em": "2026-11-05T12:00:00Z", "op_cdc": "U"},
            {"pedido_id": "PED-1002", "cliente_id": "CLI-002", "categoria_produto": "Esportes", "valor_centavos": 45900, "status_origem": "DELIVERED", "criado_em": "2026-11-10T15:10:00Z", "op_cdc": "I"},
            {"pedido_id": "PED-1003", "cliente_id": "CLI-003", "categoria_produto": "Casa & Jardim", "valor_centavos": 89000, "status_origem": "SHIPPED", "criado_em": "2026-11-18T18:40:00Z", "op_cdc": "I"},
            {"pedido_id": "PED-1004", "cliente_id": "CLI-004", "categoria_produto": "Livros", "valor_centavos": 12500, "status_origem": "DELIVERED", "criado_em": "2026-08-12T08:30:00Z", "op_cdc": "I"},
        ]
    )

    df_clientes_val = SCHEMA_CLIENTES.validate(df_clientes)
    df_pedidos_val = SCHEMA_PEDIDOS.validate(df_pedidos)

    gravar_tabela_bronze(df_clientes_val, "oltp_clientes_cdc", "postgres_erp_cdc")
    gravar_tabela_bronze(df_pedidos_val, "oltp_pedidos_cdc", "postgres_erp_cdc")


if __name__ == "__main__":
    executar_ingestao_relacional()
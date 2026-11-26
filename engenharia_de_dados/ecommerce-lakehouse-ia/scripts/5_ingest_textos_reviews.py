import pandas as pd
import pandera as pa
from pandera import Column, Check
from bronze_writer import gravar_tabela_bronze


SCHEMA_TEXTOS = pa.DataFrameSchema(
    {
        "documento_id": Column(str, nullable=False),
        "tipo_documento": Column(str, Check.isin(["review_produto", "ticket_suporte", "politica_interna"]), nullable=False),
        "cliente_id": Column(str, nullable=True),
        "pedido_id": Column(str, nullable=True),
        "nota_avaliacao": Column("Int64", Check.in_range(1, 5), nullable=True, coerce=True),
        "texto_bruto": Column(str, Check.str_length(min_value=5), nullable=False),
        "criado_em": Column(str, nullable=False),
    }
)


def executar_ingestao_textos() -> None:
    documentos = [
        {"documento_id": "DOC-01", "tipo_documento": "review_produto", "cliente_id": "CLI-001", "pedido_id": "PED-1001", "nota_avaliacao": 5, "texto_bruto": "Entrega super rápida e produto bem embalado! Meu CPF 123.456.789-01 estava na nota fiscal certinho.", "criado_em": "2026-11-07T10:00:00Z"},
        {"documento_id": "DOC-02", "tipo_documento": "ticket_suporte", "cliente_id": "CLI-004", "pedido_id": "PED-1004", "nota_avaliacao": 2, "texto_bruto": "Demorou muito para atualizar o rastreio, quero cancelar minha assinatura. Contato: diego@email.com", "criado_em": "2026-08-20T16:00:00Z"},
        {"documento_id": "DOC-03", "tipo_documento": "politica_interna", "cliente_id": None, "pedido_id": None, "nota_avaliacao": None, "texto_bruto": "Política de Trocas e Devoluções: O cliente tem até 7 dias corridos após o recebimento para solicitar devolução integral sem custo.", "criado_em": "2026-01-10T08:00:00Z"},
    ]

    df_val = SCHEMA_TEXTOS.validate(pd.DataFrame(documentos))
    gravar_tabela_bronze(df_val, "api_documentos_textuais", "zendesk_reviews_api")


if __name__ == "__main__":
    executar_ingestao_textos()
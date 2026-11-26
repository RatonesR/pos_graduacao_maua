select
    documento_id,
    tipo_documento,
    cliente_id,
    pedido_id,
    nota_avaliacao,
    regexp_replace(
        regexp_replace(texto_bruto, '[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}', '[CPF_OCULTO]', 'g'),
        '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        '[EMAIL_OCULTO]',
        'g'
    ) as texto_sanitizado,
    cast(criado_em as timestamp) as criado_em
from read_parquet('s3://bronze/bronze.db/api_documentos_textuais/data/*/*.parquet')
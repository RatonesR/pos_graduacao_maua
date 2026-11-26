with raw_pedidos as (
    select *
    from read_parquet('s3://bronze/bronze.db/oltp_pedidos_cdc/data/*/*.parquet')
),
deduplicado as (
    select
        pedido_id,
        cliente_id,
        categoria_produto,
        round(valor_centavos / 100.0, 2) as valor_brl,
        upper(status_origem) as status_pedido,
        cast(criado_em as timestamp) as criado_em,
        op_cdc,
        row_number() over (
            partition by pedido_id
            order by _ingerido_em desc, case when op_cdc = 'U' then 1 else 2 end
        ) as rn
    from raw_pedidos
)
select
    pedido_id,
    cliente_id,
    categoria_produto,
    valor_brl,
    status_pedido,
    criado_em
from deduplicado
where rn = 1
  and op_cdc != 'D'
with raw_clientes as (
    select *
    from read_parquet('s3://bronze/bronze.db/oltp_clientes_cdc/data/*/*.parquet')
),
deduplicado as (
    select
        cliente_id,
        nome_completo,
        concat('***.***.', substr(cpf, 7, 3), '-', substr(cpf, 10, 2)) as cpf_mascarado,
        lower(trim(email)) as email,
        upper(uf) as uf,
        segmento,
        op_cdc,
        cast(atualizado_em as timestamp) as atualizado_em,
        row_number() over (
            partition by cliente_id
            order by cast(atualizado_em as timestamp) desc
        ) as rn
    from raw_clientes
)
select
    cliente_id,
    nome_completo,
    cpf_mascarado,
    email,
    uf,
    segmento,
    atualizado_em
from deduplicado
where rn = 1
  and op_cdc != 'D'
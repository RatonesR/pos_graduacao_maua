with clickstream_dedup as (
    select distinct
        evento_id,
        sessao_id,
        cliente_id,
        tipo_evento,
        dispositivo,
        duracao_segundos,
        cast(evento_timestamp as timestamp) as evento_timestamp
    from read_parquet('s3://bronze/bronze.db/stream_clickstream_eventos/data/*/*.parquet')
),
iot_limpo as (
    select
        leitura_id,
        veiculo_id,
        pedido_id,
        temperatura_celsius,
        vibracao_g,
        velocidade_kmh,
        case
            when temperatura_celsius > 15.0 or vibracao_g > 1.5 then true
            else false
        end as alerta_risco_carga,
        cast(leitura_timestamp as timestamp) as leitura_timestamp
    from read_parquet('s3://bronze/bronze.db/iot_telemetria_frota/data/*/*.parquet')
    where temperatura_celsius between -30.0 and 60.0
)
select
    c.cliente_id,
    count(distinct c.sessao_id) as total_sessoes,
    count(c.evento_id) as total_eventos_navegacao,
    sum(case when c.tipo_evento = 'checkout_abandon' then 1 else 0 end) as total_abandonos_carrinho,
    avg(c.duracao_segundos) as tempo_medio_navegacao_seg
from clickstream_dedup c
where c.cliente_id is not null
group by c.cliente_id
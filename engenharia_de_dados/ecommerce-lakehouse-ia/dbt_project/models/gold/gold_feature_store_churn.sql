with clientes as (
    select * from {{ ref('slv_clientes') }}
),
pedidos_agg as (
    select
        cliente_id,
        count(pedido_id) as qtd_pedidos,
        coalesce(sum(valor_brl), 0) as receita_total_brl,
        coalesce(avg(valor_brl), 0) as ticket_medio_brl,
        max(criado_em) as ultima_compra_em
    from {{ ref('slv_pedidos') }}
    group by cliente_id
),
navegacao as (
    select * from {{ ref('slv_clickstream_telemetria') }}
),
reviews as (
    select
        cliente_id,
        avg(nota_avaliacao) as nota_media_avaliacao,
        count(documento_id) as qtd_interacoes_suporte
    from {{ ref('slv_documentos_nlp') }}
    where cliente_id is not null
    group by cliente_id
)
select
    c.cliente_id,
    c.uf,
    c.segmento,
    coalesce(p.qtd_pedidos, 0) as qtd_pedidos,
    coalesce(p.receita_total_brl, 0.0) as receita_total_brl,
    coalesce(p.ticket_medio_brl, 0.0) as ticket_medio_brl,
    coalesce(n.total_sessoes, 0) as total_sessoes,
    coalesce(n.total_abandonos_carrinho, 0) as total_abandonos_carrinho,
    coalesce(n.tempo_medio_navegacao_seg, 0.0) as tempo_medio_navegacao_seg,
    coalesce(r.nota_media_avaliacao, 5.0) as nota_media_avaliacao,
    case
        when coalesce(n.total_abandonos_carrinho, 0) >= 1 and coalesce(r.nota_media_avaliacao, 5.0) <= 3.0 then 1
        else 0
    end as flag_risco_churn
from clientes c
left join pedidos_agg p on c.cliente_id = p.cliente_id
left join navegacao n on c.cliente_id = n.cliente_id
left join reviews r on c.cliente_id = r.cliente_id
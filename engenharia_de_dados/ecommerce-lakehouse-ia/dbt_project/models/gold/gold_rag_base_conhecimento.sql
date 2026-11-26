select
    d.documento_id,
    d.tipo_documento,
    d.cliente_id,
    c.segmento as segmento_cliente,
    d.pedido_id,
    p.categoria_produto,
    d.nota_avaliacao,
    d.texto_sanitizado as conteudo_contextualizado,
    d.criado_em
from {{ ref('slv_documentos_nlp') }} d
left join {{ ref('slv_clientes') }} c on d.cliente_id = c.cliente_id
left join {{ ref('slv_pedidos') }} p on d.pedido_id = p.pedido_id
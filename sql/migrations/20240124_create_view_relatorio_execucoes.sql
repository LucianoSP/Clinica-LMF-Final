-- Cria uma view para o relatório de execuções
CREATE OR REPLACE VIEW vw_relatorio_execucoes AS
SELECT 
    e.id::uuid,
    e.data_execucao,
    e.data_atendimento,
    e.paciente_nome,
    e.paciente_carteirinha,
    e.numero_guia,
    e.codigo_ficha,
    e.origem,
    e.status_biometria,
    e.profissional_executante,
    COALESCE(e.conselho_profissional || ' ' || e.numero_conselho || '/' || e.uf_conselho, '-') as registro_conselho,
    e.codigo_cbo,
    g.data_solicitacao as data_solicitacao_guia,
    g.data_autorizacao as data_autorizacao_guia,
    g.quantidade_autorizada,
    g.quantidade_executada,
    g.status as status_guia,
    p.codigo as codigo_procedimento,
    p.nome as nome_procedimento,
    p.valor as valor_procedimento,
    ps.nome as plano_saude,
    ps.registro_ans,
    e.created_at,
    e.created_by::uuid,
    e.updated_at,
    e.updated_by::uuid
FROM 
    execucoes e
    LEFT JOIN guias g ON e.guia_id = g.id
    LEFT JOIN procedimentos p ON g.procedimento_id = p.id
    LEFT JOIN carteirinhas c ON g.carteirinha_id = c.id
    LEFT JOIN planos_saude ps ON c.plano_saude_id = ps.id
WHERE 
    e.deleted_at IS NULL;
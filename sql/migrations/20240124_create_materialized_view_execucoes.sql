-- Cria uma view materializada para as execuções
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_execucoes AS
SELECT 
    e.id::uuid,
    e.guia_id::uuid,
    e.sessao_id::uuid,
    e.data_execucao,
    e.data_atendimento,
    e.paciente_nome,
    e.paciente_carteirinha,
    e.numero_guia,
    e.codigo_ficha,
    e.codigo_ficha_temp,
    e.usuario_executante::uuid,
    e.origem,
    e.ip_origem,
    e.ordem_execucao,
    e.status_biometria,
    e.conselho_profissional,
    e.numero_conselho,
    e.uf_conselho,
    e.codigo_cbo,
    e.profissional_executante,
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
    e.updated_by::uuid,
    e.deleted_at
FROM 
    execucoes e
    LEFT JOIN guias g ON e.guia_id = g.id
    LEFT JOIN procedimentos p ON g.procedimento_id = p.id
    LEFT JOIN carteirinhas c ON g.carteirinha_id = c.id
    LEFT JOIN planos_saude ps ON c.plano_saude_id = ps.id
WHERE 
    e.deleted_at IS NULL;

-- Cria índices para melhorar a performance das consultas mais comuns
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_data ON mv_execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_paciente ON mv_execucoes(paciente_nome);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_carteirinha ON mv_execucoes(paciente_carteirinha);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_guia ON mv_execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_profissional ON mv_execucoes(profissional_executante);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_status ON mv_execucoes(status_biometria);

-- Função para atualizar a view materializada
CREATE OR REPLACE FUNCTION refresh_mv_execucoes()
RETURNS trigger AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar a view materializada quando houver mudanças
DROP TRIGGER IF EXISTS trigger_refresh_mv_execucoes ON execucoes;
CREATE TRIGGER trigger_refresh_mv_execucoes
    AFTER INSERT OR UPDATE OR DELETE
    ON execucoes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_mv_execucoes();
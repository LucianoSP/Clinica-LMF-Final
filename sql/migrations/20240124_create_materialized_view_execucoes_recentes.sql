-- Cria uma view materializada para as execuções recentes (últimos 90 dias)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_execucoes_recentes AS
SELECT *
FROM mv_execucoes
WHERE data_execucao >= CURRENT_DATE - INTERVAL '90 days';

-- Cria índices específicos para a view de execuções recentes
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_recentes_data ON mv_execucoes_recentes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_recentes_paciente ON mv_execucoes_recentes(paciente_nome);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_recentes_guia ON mv_execucoes_recentes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_mv_execucoes_recentes_profissional ON mv_execucoes_recentes(profissional_executante);

-- Função para atualizar a view materializada de execuções recentes
CREATE OR REPLACE FUNCTION refresh_mv_execucoes_recentes()
RETURNS trigger AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes_recentes;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar a view materializada quando houver mudanças
DROP TRIGGER IF EXISTS trigger_refresh_mv_execucoes_recentes ON execucoes;
CREATE TRIGGER trigger_refresh_mv_execucoes_recentes
    AFTER INSERT OR UPDATE OR DELETE
    ON execucoes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_mv_execucoes_recentes();
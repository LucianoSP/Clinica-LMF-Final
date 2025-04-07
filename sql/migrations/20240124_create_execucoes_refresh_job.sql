-- Extensão para gerenciar jobs no PostgreSQL
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Job para atualizar as views materializadas a cada 30 minutos
SELECT cron.schedule(
    'refresh_execucoes_views',   -- nome do job
    '*/30 * * * *',             -- expressão cron (a cada 30 minutos)
    'SELECT refresh_execucoes_views_manual();'  -- comando SQL a ser executado
);

-- Criar função para atualização manual das views
CREATE OR REPLACE FUNCTION refresh_execucoes_views_manual()
RETURNS void AS $$
BEGIN
    -- Atualiza a view principal
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes;
    -- Atualiza a view de execuções recentes
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes_recentes;
END;
$$ LANGUAGE plpgsql;
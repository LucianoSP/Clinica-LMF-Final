-- Configuração do pg_cron para atualização das views materializadas de execuções

-- Habilitar a extensão pg_cron (requer privilégios de superusuário)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Garantir que o usuário da aplicação tenha acesso ao pg_cron
GRANT USAGE ON SCHEMA cron TO authenticated;

-- Remover jobs existentes se houver
SELECT cron.unschedule('refresh_execucoes_views');

-- Criar o job para atualizar as views a cada 30 minutos
SELECT cron.schedule(
    'refresh_execucoes_views',
    '*/30 * * * *',
    $$
    BEGIN;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes_recentes;
    COMMIT;
    $$
);

-- Criar a função que pode ser chamada manualmente
CREATE OR REPLACE FUNCTION refresh_execucoes_views_manual()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes_recentes;
END;
$$ LANGUAGE plpgsql;

-- Garantir que o usuário da aplicação possa executar a função manual
GRANT EXECUTE ON FUNCTION refresh_execucoes_views_manual() TO authenticated;
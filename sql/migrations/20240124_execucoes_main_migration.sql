-- Migration principal para executar todos os scripts relacionados às execuções

-- 0. Cria a estrutura base da tabela
\i migrations/20240124_execucoes_schema.sql

-- 1. Remove as views e ajusta os tipos das colunas para UUID
\i migrations/20240124_fix_uuid_columns_execucoes.sql

-- 2. Adiciona as novas colunas do profissional
\i migrations/20240124_add_profissional_columns_execucoes.sql

-- 3. Popula dados de exemplo (antes de criar as views para melhor performance)
\i migrations/20240124_populate_execucoes.sql

-- 4. Cria a view do relatório
\i migrations/20240124_create_view_relatorio_execucoes.sql

-- 5. Cria a view materializada para otimização
\i migrations/20240124_create_materialized_view_execucoes.sql

-- 6. Cria a view materializada para execuções recentes
\i migrations/20240124_create_materialized_view_execucoes_recentes.sql

-- 7. Criar função de atualização manual (sem depender do pg_cron)
CREATE OR REPLACE FUNCTION refresh_execucoes_views_manual()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_execucoes_recentes;
END;
$$ LANGUAGE plpgsql;

-- 8. Atualiza as views materializadas com os dados inseridos
SELECT refresh_execucoes_views_manual();
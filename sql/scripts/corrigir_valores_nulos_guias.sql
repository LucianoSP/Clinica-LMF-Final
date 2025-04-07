-- Script para corrigir valores nulos nas guias
-- Este script verifica e corrige valores nulos nos campos data_solicitacao, dados_autorizacao e historico_status

-- Primeiro, vamos verificar quantas guias têm valores nulos
SELECT 
    COUNT(*) as total_guias,
    COUNT(*) FILTER (WHERE data_solicitacao IS NULL) as guias_sem_data_solicitacao,
    COUNT(*) FILTER (WHERE dados_autorizacao IS NULL) as guias_sem_dados_autorizacao,
    COUNT(*) FILTER (WHERE historico_status IS NULL) as guias_sem_historico_status
FROM guias
WHERE deleted_at IS NULL;

-- Agora, vamos corrigir os valores nulos
BEGIN;

-- Corrigir data_solicitacao nula usando created_at
UPDATE guias
SET data_solicitacao = created_at::date
WHERE data_solicitacao IS NULL
AND deleted_at IS NULL;

-- Corrigir dados_autorizacao nulo usando um objeto vazio
UPDATE guias
SET dados_autorizacao = '{}'::jsonb
WHERE dados_autorizacao IS NULL
AND deleted_at IS NULL;

-- Corrigir historico_status nulo usando um array vazio
UPDATE guias
SET historico_status = '[]'::jsonb
WHERE historico_status IS NULL
AND deleted_at IS NULL;

-- Verificar novamente para confirmar que não há mais valores nulos
SELECT 
    COUNT(*) as total_guias,
    COUNT(*) FILTER (WHERE data_solicitacao IS NULL) as guias_sem_data_solicitacao,
    COUNT(*) FILTER (WHERE dados_autorizacao IS NULL) as guias_sem_dados_autorizacao,
    COUNT(*) FILTER (WHERE historico_status IS NULL) as guias_sem_historico_status
FROM guias
WHERE deleted_at IS NULL;

COMMIT;

-- Adicionar comentário para confirmar que o script foi executado
COMMENT ON TABLE guias IS 'Tabela de guias. Valores nulos corrigidos em ' || NOW()::text; 
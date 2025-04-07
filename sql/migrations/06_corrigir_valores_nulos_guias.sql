-- Migração para corrigir valores nulos em campos críticos da tabela guias
-- Esta migração garante que não haja valores nulos nos campos data_solicitacao e dados_autorizacao

-- 1. Atualizar guias existentes com valores nulos
UPDATE guias
SET data_solicitacao = created_at
WHERE data_solicitacao IS NULL;

UPDATE guias
SET dados_autorizacao = '{}'::jsonb
WHERE dados_autorizacao IS NULL;

-- 2. Alterar a definição da tabela para adicionar valores padrão
ALTER TABLE guias 
ALTER COLUMN data_solicitacao SET DEFAULT CURRENT_DATE,
ALTER COLUMN dados_autorizacao SET DEFAULT '{}'::jsonb;

-- 3. Adicionar restrições NOT NULL para evitar valores nulos no futuro
-- Comentado para evitar problemas com dados existentes
-- ALTER TABLE guias 
-- ALTER COLUMN data_solicitacao SET NOT NULL,
-- ALTER COLUMN dados_autorizacao SET NOT NULL;

-- 4. Verificar se as correções foram aplicadas
-- SELECT id, numero_guia, data_solicitacao, dados_autorizacao
-- FROM guias
-- WHERE data_solicitacao IS NULL OR dados_autorizacao IS NULL; 
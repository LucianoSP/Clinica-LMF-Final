-- Desabilitar temporariamente as restrições de chave estrangeira
SET session_replication_role = 'replica';

-- Adicionar a coluna procedimento_id
ALTER TABLE guias
ADD COLUMN IF NOT EXISTS procedimento_id uuid REFERENCES procedimentos(id);

-- Criar índice para melhorar performance
CREATE INDEX IF NOT EXISTS idx_guias_procedimento ON guias(procedimento_id);

-- Reabilitar as restrições de chave estrangeira
SET session_replication_role = 'origin';

-- Comentário para rollback se necessário
-- Para reverter:
-- DROP INDEX IF EXISTS idx_guias_procedimento;
-- ALTER TABLE guias DROP COLUMN IF EXISTS procedimento_id; 
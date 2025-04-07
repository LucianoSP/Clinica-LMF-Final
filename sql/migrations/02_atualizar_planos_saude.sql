-- Desabilitar temporariamente as restrições de chave estrangeira
SET session_replication_role = 'replica';

-- Backup da tabela existente
CREATE TABLE planos_saude_backup AS SELECT * FROM planos_saude;

-- Remover as constraints antigas
ALTER TABLE planos_saude 
    DROP CONSTRAINT IF EXISTS planos_saude_created_by_fkey,
    DROP CONSTRAINT IF EXISTS planos_saude_updated_by_fkey;

-- Adicionar as novas foreign keys para auth.users
ALTER TABLE planos_saude
    ADD CONSTRAINT planos_saude_created_by_fkey 
    FOREIGN KEY (created_by) 
    REFERENCES auth.users(id),
    ADD CONSTRAINT planos_saude_updated_by_fkey 
    FOREIGN KEY (updated_by) 
    REFERENCES auth.users(id);

-- Garantir que as colunas podem ser nulas
ALTER TABLE planos_saude 
    ALTER COLUMN created_by DROP NOT NULL,
    ALTER COLUMN updated_by DROP NOT NULL;

-- Reabilitar as restrições de chave estrangeira
SET session_replication_role = 'origin';

-- Comentário para rollback se necessário
-- Para reverter:
-- ALTER TABLE planos_saude 
--     DROP CONSTRAINT planos_saude_created_by_fkey,
--     DROP CONSTRAINT planos_saude_updated_by_fkey;
-- DROP TABLE planos_saude_backup; 
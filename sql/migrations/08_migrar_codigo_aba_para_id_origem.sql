-- Migração para consolidar 'codigo_aba' em 'id_origem'
-- Execute este script para transferir dados e preparar para a remoção do campo redundante

-- 1. Certificar que todos os pacientes tenham id_origem preenchido (copiando de codigo_aba se necessário)
UPDATE pacientes 
SET id_origem = codigo_aba 
WHERE (id_origem IS NULL OR id_origem = '') 
AND codigo_aba IS NOT NULL;

-- 2. Tornar id_origem UNIQUE e NOT NULL, como codigo_aba era
ALTER TABLE pacientes
ALTER COLUMN id_origem SET NOT NULL;

-- 3. Adicionar constraint UNIQUE para id_origem se não existir
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'pacientes_id_origem_key' 
        AND conrelid = 'pacientes'::regclass
    ) THEN
        ALTER TABLE pacientes ADD CONSTRAINT pacientes_id_origem_key UNIQUE (id_origem);
    END IF;
END
$$;

-- 4. Atualizar comentário da coluna
COMMENT ON COLUMN pacientes.id_origem IS 'Código único para vinculação com sistemas externos (antigo codigo_aba)';

-- 5. Criar índice para id_origem se ainda não existir
CREATE INDEX IF NOT EXISTS idx_pacientes_id_origem ON pacientes(id_origem);

-- Após validar que todos os dados foram migrados corretamente, execute:
-- ALTER TABLE pacientes DROP COLUMN codigo_aba;
-- DROP INDEX IF EXISTS idx_pacientes_codigo_aba; 
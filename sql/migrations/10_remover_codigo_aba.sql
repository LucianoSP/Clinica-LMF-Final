-- Migração para remover completamente o campo codigo_aba da tabela pacientes
-- Esta migração remove o campo que foi substituído pelo campo id_origem

-- 1. Verificar se existem pacientes sem id_origem
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem IS NULL OR id_origem = '') as pacientes_sem_id_origem
FROM pacientes
WHERE deleted_at IS NULL;

-- 2. Verificar se o índice para codigo_aba ainda existe
SELECT indexname 
FROM pg_indexes 
WHERE tablename = 'pacientes' 
AND indexname = 'idx_pacientes_codigo_aba';

-- 3. Remover o índice do campo codigo_aba se existir
DROP INDEX IF EXISTS idx_pacientes_codigo_aba;

-- 4. Verificar se a coluna codigo_aba ainda existe
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'pacientes' 
AND column_name = 'codigo_aba';

-- 5. Remover o campo codigo_aba da tabela pacientes se existir
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'pacientes' 
        AND column_name = 'codigo_aba'
    ) THEN
        ALTER TABLE pacientes DROP COLUMN codigo_aba;
    END IF;
END $$;

-- 6. Verificar novamente para confirmar que a migração foi bem-sucedida
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem IS NULL OR id_origem = '') as pacientes_sem_id_origem
FROM pacientes
WHERE deleted_at IS NULL; 
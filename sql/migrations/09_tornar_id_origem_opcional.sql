-- Migração para tornar o campo id_origem opcional na tabela pacientes
-- Esta migração reverte a restrição NOT NULL adicionada anteriormente

-- 1. Verificar quantos pacientes têm id_origem preenchido
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem IS NULL OR id_origem = '') as pacientes_sem_id_origem
FROM pacientes
WHERE deleted_at IS NULL;

-- 2. Remover a restrição NOT NULL do campo id_origem
ALTER TABLE pacientes
ALTER COLUMN id_origem DROP NOT NULL;

-- 3. Remover a restrição UNIQUE existente e adicionar uma que permita valores NULL
-- Primeiro, verificar se a constraint existe
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'pacientes_id_origem_key' 
        AND conrelid = 'pacientes'::regclass
    ) THEN
        -- Remover a constraint existente
        ALTER TABLE pacientes DROP CONSTRAINT pacientes_id_origem_key;
        
        -- Adicionar uma nova constraint que ignore valores NULL
        ALTER TABLE pacientes ADD CONSTRAINT pacientes_id_origem_key UNIQUE (id_origem);
    END IF;
END
$$;

-- 4. Atualizar comentário da coluna
COMMENT ON COLUMN pacientes.id_origem IS 'Código opcional para vinculação com sistemas externos (antigo codigo_aba)';

-- 5. Verificar novamente para confirmar que a alteração foi aplicada
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem IS NULL OR id_origem = '') as pacientes_sem_id_origem
FROM pacientes
WHERE deleted_at IS NULL; 
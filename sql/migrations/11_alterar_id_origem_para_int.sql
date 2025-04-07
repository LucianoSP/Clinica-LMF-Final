-- Migração para alterar o tipo do campo id_origem de VARCHAR para INT na tabela pacientes
-- Esta migração alinha o campo com a definição no script 01_criar_tabelas.sql

-- 1. Verificar o tipo atual do campo id_origem
DO $$
DECLARE
    coluna_tipo TEXT;
BEGIN
    SELECT data_type INTO coluna_tipo
    FROM information_schema.columns
    WHERE table_name = 'pacientes' AND column_name = 'id_origem';
    
    RAISE NOTICE 'Tipo atual do campo id_origem: %', coluna_tipo;
END $$;

-- 2. Verificar quantos pacientes têm id_origem que não pode ser convertido para INT
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem ~ '^[0-9]+$' OR id_origem IS NULL) as pacientes_conversiveis,
    COUNT(*) FILTER (WHERE id_origem !~ '^[0-9]+$' AND id_origem IS NOT NULL) as pacientes_nao_conversiveis
FROM pacientes
WHERE deleted_at IS NULL;

-- 3. Criar uma tabela temporária para armazenar IDs de registros problemáticos
CREATE TEMP TABLE pacientes_id_origem_problematicos AS
SELECT id, id_origem
FROM pacientes
WHERE id_origem !~ '^[0-9]+$' AND id_origem IS NOT NULL AND deleted_at IS NULL;

-- 4. Exibir registros problemáticos (se houver)
SELECT * FROM pacientes_id_origem_problematicos;

-- 5. Atualizar registros problemáticos para NULL (opcional - descomente se necessário)
-- UPDATE pacientes
-- SET id_origem = NULL
-- WHERE id IN (SELECT id FROM pacientes_id_origem_problematicos);

-- 6. Alterar o tipo do campo id_origem para INT
ALTER TABLE pacientes
ALTER COLUMN id_origem TYPE INT USING (
    CASE 
        WHEN id_origem ~ '^[0-9]+$' THEN id_origem::INT
        ELSE NULL
    END
);

-- 7. Recriar o índice para o campo id_origem
DROP INDEX IF EXISTS idx_pacientes_id_origem;
CREATE INDEX idx_pacientes_id_origem ON pacientes(id_origem);

-- 8. Atualizar comentário da coluna
COMMENT ON COLUMN pacientes.id_origem IS 'Código numérico opcional para vinculação com sistemas externos';

-- 9. Verificar o tipo após a alteração
DO $$
DECLARE
    coluna_tipo TEXT;
BEGIN
    SELECT data_type INTO coluna_tipo
    FROM information_schema.columns
    WHERE table_name = 'pacientes' AND column_name = 'id_origem';
    
    RAISE NOTICE 'Novo tipo do campo id_origem: %', coluna_tipo;
END $$;

-- 10. Verificar quantos pacientes têm id_origem após a conversão
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE id_origem IS NOT NULL) as pacientes_com_id_origem,
    COUNT(*) FILTER (WHERE id_origem IS NULL) as pacientes_sem_id_origem
FROM pacientes
WHERE deleted_at IS NULL;

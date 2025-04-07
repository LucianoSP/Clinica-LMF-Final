-- Script para corrigir valores nulos nos pacientes
-- Este script verifica e corrige valores nulos nos campos created_by e updated_by

-- Primeiro, vamos verificar quantos pacientes têm valores nulos
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE created_by IS NULL) as pacientes_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as pacientes_sem_updated_by
FROM pacientes
WHERE deleted_at IS NULL;

-- Agora, vamos corrigir os valores nulos
BEGIN;

-- Buscar o primeiro usuário administrador
DO $$
DECLARE
    admin_id UUID;
BEGIN
    -- Buscar o primeiro usuário administrador
    SELECT id INTO admin_id FROM usuarios WHERE tipo_usuario = 'admin' LIMIT 1;
    
    -- Se não encontrar um administrador, usar o primeiro usuário
    IF admin_id IS NULL THEN
        SELECT id INTO admin_id FROM usuarios LIMIT 1;
    END IF;
    
    -- Atualizar os registros com valores nulos
    IF admin_id IS NOT NULL THEN
        UPDATE pacientes
        SET created_by = admin_id
        WHERE created_by IS NULL;
        
        UPDATE pacientes
        SET updated_by = admin_id
        WHERE updated_by IS NULL;
        
        RAISE NOTICE 'Pacientes atualizados com o usuário ID: %', admin_id;
    ELSE
        RAISE EXCEPTION 'Não foi possível encontrar um usuário para atualizar os pacientes';
    END IF;
END $$;

-- Verificar novamente para confirmar que não há mais valores nulos
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(*) FILTER (WHERE created_by IS NULL) as pacientes_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as pacientes_sem_updated_by
FROM pacientes
WHERE deleted_at IS NULL;

COMMIT;

-- Adicionar comentário para confirmar que o script foi executado
COMMENT ON TABLE pacientes IS 'Tabela de pacientes. Valores nulos corrigidos em ' || NOW()::text; 
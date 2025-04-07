-- Script para corrigir valores nulos nas carteirinhas
-- Este script verifica e corrige valores nulos nos campos created_by e updated_by

-- Primeiro, vamos verificar quantas carteirinhas têm valores nulos
SELECT 
    COUNT(*) as total_carteirinhas,
    COUNT(*) FILTER (WHERE created_by IS NULL) as carteirinhas_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as carteirinhas_sem_updated_by
FROM carteirinhas
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
        UPDATE carteirinhas
        SET created_by = admin_id
        WHERE created_by IS NULL;
        
        UPDATE carteirinhas
        SET updated_by = admin_id
        WHERE updated_by IS NULL;
        
        RAISE NOTICE 'Carteirinhas atualizadas com o usuário ID: %', admin_id;
    ELSE
        RAISE EXCEPTION 'Não foi possível encontrar um usuário para atualizar as carteirinhas';
    END IF;
END $$;

-- Verificar novamente para confirmar que não há mais valores nulos
SELECT 
    COUNT(*) as total_carteirinhas,
    COUNT(*) FILTER (WHERE created_by IS NULL) as carteirinhas_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as carteirinhas_sem_updated_by
FROM carteirinhas
WHERE deleted_at IS NULL;

COMMIT;

-- Adicionar comentário para confirmar que o script foi executado
COMMENT ON TABLE carteirinhas IS 'Tabela de carteirinhas. Valores nulos corrigidos em ' || NOW()::text; 
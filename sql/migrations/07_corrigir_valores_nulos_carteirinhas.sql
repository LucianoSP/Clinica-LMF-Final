-- Migração para corrigir valores nulos em campos críticos da tabela carteirinhas
-- Esta migração garante que não haja valores nulos nos campos created_by e updated_by

-- 1. Primeiro, vamos verificar quantas carteirinhas têm valores nulos
SELECT 
    COUNT(*) as total_carteirinhas,
    COUNT(*) FILTER (WHERE created_by IS NULL) as carteirinhas_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as carteirinhas_sem_updated_by
FROM carteirinhas
WHERE deleted_at IS NULL;

-- 2. Atualizar carteirinhas existentes com valores nulos
-- Vamos usar o ID do primeiro usuário administrador como valor padrão
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

-- 3. Modificar o modelo Carteirinha no backend para aceitar valores nulos
-- Isso deve ser feito no arquivo backend/models/carteirinha.py
-- Alterar:
--   created_by: str
--   updated_by: str
-- Para:
--   created_by: Optional[str] = None
--   updated_by: Optional[str] = None

-- 4. Verificar novamente para confirmar que não há mais valores nulos
SELECT 
    COUNT(*) as total_carteirinhas,
    COUNT(*) FILTER (WHERE created_by IS NULL) as carteirinhas_sem_created_by,
    COUNT(*) FILTER (WHERE updated_by IS NULL) as carteirinhas_sem_updated_by
FROM carteirinhas
WHERE deleted_at IS NULL; 
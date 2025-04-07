-- Migração para sincronizar o usuário sistema entre as tabelas 'usuarios' e 'auth.users'
-- Criação: 27/06/2024

-- 1. Verificamos se o usuário sistema já existe em auth.users
DO $$
DECLARE
    sistema_uuid UUID := '00000000-0000-0000-0000-000000000000';
    sistema_email VARCHAR := 'sistema@sistema.com';
    user_exists BOOLEAN;
BEGIN
    -- Verificar se o usuário já existe na tabela auth.users
    SELECT EXISTS (
        SELECT 1 FROM auth.users WHERE id = sistema_uuid
    ) INTO user_exists;

    -- Se não existe, criamos o usuário na tabela auth.users
    IF NOT user_exists THEN
        INSERT INTO auth.users (
            id,
            email,
            raw_user_meta_data,
            created_at,
            updated_at
        ) VALUES (
            sistema_uuid,
            sistema_email,
            jsonb_build_object(
                'nome', 'Sistema',
                'role', 'sistema'
            ),
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'Usuário sistema criado em auth.users com ID %', sistema_uuid;
    ELSE
        RAISE NOTICE 'Usuário sistema já existe em auth.users com ID %', sistema_uuid;
    END IF;

    -- Verificar se o usuário já existe na tabela usuarios
    SELECT EXISTS (
        SELECT 1 FROM usuarios WHERE id = sistema_uuid
    ) INTO user_exists;

    -- Se não existe, criamos o usuário na tabela usuarios
    IF NOT user_exists THEN
        INSERT INTO usuarios (
            id,
            auth_user_id,
            nome,
            email,
            tipo_usuario,
            ativo,
            created_at,
            updated_at
        ) VALUES (
            sistema_uuid,
            sistema_uuid,
            'Sistema',
            sistema_email,
            'admin',
            true,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'Usuário sistema criado em usuarios com ID %', sistema_uuid;
    ELSE
        RAISE NOTICE 'Usuário sistema já existe em usuarios com ID %', sistema_uuid;
    END IF;
END $$; 
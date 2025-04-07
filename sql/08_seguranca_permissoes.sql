--================ CONFIGURAÇÕES DE SEGURANÇA E PERMISSÕES =================

-- IMPORTANTE: No Supabase, o RLS (Row Level Security) é habilitado por padrão
-- e pode causar problemas de "permission denied" mesmo para administradores.
-- Considere usar as funções auxiliares do Supabase ou desabilitar RLS se necessário.

-- Exemplo de desabilitação de RLS para todas as tabelas (NÃO RECOMENDADO EM PRODUÇÃO)
/*
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        BEGIN
            EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY;', r.tablename);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao desabilitar RLS para tabela %: %', r.tablename, SQLERRM;
        END;
    END LOOP;
END $$;
*/

-- Exemplo de habilitação de RLS e criação de políticas permissivas (Abordagem mais comum no Supabase)
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        BEGIN
            -- Habilitar RLS (se ainda não estiver)
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', r.tablename);
            
            -- Remover políticas antigas (se existirem) para evitar conflitos
            EXECUTE format('DROP POLICY IF EXISTS "Permitir acesso total para autenticados" ON public.%I;', r.tablename);
            EXECUTE format('DROP POLICY IF EXISTS "Permitir acesso total para service_role" ON public.%I;', r.tablename);
            EXECUTE format('DROP POLICY IF EXISTS "Permitir leitura para anônimos" ON public.%I;', r.tablename);
             EXECUTE format('DROP POLICY IF EXISTS all_access ON public.%I;', r.tablename); -- Remove a política antiga

            -- Criar política que permite acesso total para usuários autenticados
            EXECUTE format('
                CREATE POLICY "Permitir acesso total para autenticados" ON public.%I 
                FOR ALL 
                TO authenticated 
                USING (true) 
                WITH CHECK (true);', 
                r.tablename
            );
            
            -- (Opcional) Política para service_role (geralmente já tem acesso)
            -- EXECUTE format('
            --     CREATE POLICY "Permitir acesso total para service_role" ON public.%I 
            --     FOR ALL 
            --     TO service_role 
            --     USING (true) 
            --     WITH CHECK (true);', 
            --     r.tablename
            -- );
            
            -- (Opcional) Permitir leitura para usuários não autenticados (anon)
            -- EXECUTE format('
            --     CREATE POLICY "Permitir leitura para anônimos" ON public.%I 
            --     FOR SELECT 
            --     TO anon 
            --     USING (true);', 
            --     r.tablename
            -- );

        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao configurar RLS/políticas para tabela %: %', r.tablename, SQLERRM;
        END;
    END LOOP;
END $$;

-- Conceder privilégios básicos (USAGE em schema, SELECT em tabelas/sequências para anon se necessário)
-- GRANT USAGE ON SCHEMA public TO authenticated;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- GRANT USAGE ON SCHEMA public TO service_role;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- GRANT USAGE ON SCHEMA public TO anon;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Informações úteis para diagnóstico
DO $$
BEGIN
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'CONFIGURAÇÃO DE SEGURANÇA E PERMISSÕES APLICADA (via RLS policies)';
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Verifique as políticas RLS no painel do Supabase.';
    RAISE NOTICE 'Se encontrar "permission denied", revise as políticas RLS ou os privilégios GRANT.';
    RAISE NOTICE '====================================================';
END $$; 
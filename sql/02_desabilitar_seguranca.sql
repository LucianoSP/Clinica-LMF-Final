-- Script para desabilitar RLS e conceder permissões para todas as tabelas
-- Criado em: 12/03/2025
-- Este script desabilita o Row Level Security (RLS) para todas as tabelas
-- criadas pelo script 01_criar_tabelas.sql e concede permissões ALL para os usuários

DO $$
DECLARE
    tabela_record RECORD;
BEGIN
    -- Desabilitar RLS para todas as tabelas no schema public
    FOR tabela_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', tabela_record.tablename);
        RAISE NOTICE 'RLS desabilitado para tabela: %', tabela_record.tablename;
    END LOOP;
    
    -- Conceder permissões para todas as tabelas no schema public
    FOR tabela_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('GRANT ALL ON TABLE %I TO authenticated, anon, service_role', tabela_record.tablename);
        RAISE NOTICE 'Permissões TABLE concedidas para tabela: %', tabela_record.tablename;
    END LOOP;
    
    -- === INÍCIO DA ADIÇÃO: Permissões para Views ===
    -- Conceder permissões SELECT para todas as views no schema public
    FOR tabela_record IN 
        SELECT table_name -- Views são listadas em pg_views ou information_schema.views
        FROM information_schema.views
        WHERE table_schema = 'public'
    LOOP
        -- Correção: Conceder permissão para cada role separadamente
        BEGIN
            EXECUTE format('GRANT SELECT ON VIEW %I TO authenticated', tabela_record.table_name);
            EXECUTE format('GRANT SELECT ON VIEW %I TO anon', tabela_record.table_name);
            EXECUTE format('GRANT SELECT ON VIEW %I TO service_role', tabela_record.table_name);
            RAISE NOTICE 'Permissões SELECT VIEW concedidas para view: %', tabela_record.table_name;
        EXCEPTION WHEN OTHERS THEN
             RAISE NOTICE 'Erro ao conceder permissão SELECT para view %: %', tabela_record.table_name, SQLERRM;
        END;
    END LOOP;
    -- === FIM DA ADIÇÃO: Permissões para Views ===
    
    -- Conceder permissões para todas as sequências no schema public
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated, anon, service_role;
    
    -- Conceder permissão de uso do schema public
    GRANT USAGE ON SCHEMA public TO authenticated, anon, service_role;
    
    RAISE NOTICE 'Configuração de segurança concluída com sucesso!';
END $$;

-- Verificação das tabelas processadas
SELECT 
    tablename, 
    rowsecurity
FROM 
    pg_tables
WHERE 
    schemaname = 'public'
ORDER BY 
    tablename;

-- Instruções para uso:
-- 1. Execute este script no banco de dados do Supabase
-- 2. Verifique a saída para confirmar que todas as tabelas foram processadas
-- 3. A coluna rowsecurity deve mostrar "f" (false) para todas as tabelas
    GRANT EXECUTE ON FUNCTION public.func_listar_agendamentos_view(int, int, text, text, text, text) TO authenticated, anon, service_role;
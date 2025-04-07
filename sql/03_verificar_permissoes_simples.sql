-- Script para verificar configurações de permissão no banco de dados (versão simplificada)

-- 1. Verificar tabelas com RLS habilitado
SELECT 
    tablename, 
    relrowsecurity
FROM 
    pg_tables
JOIN 
    pg_class ON pg_tables.tablename = pg_class.relname
WHERE 
    schemaname = 'public' 
    AND relrowsecurity = true;

-- 2. Verificar políticas RLS existentes (versão simplificada)
SELECT 
    tablename,
    policyname
FROM 
    pg_policies
WHERE 
    schemaname = 'public'
ORDER BY 
    tablename, policyname;

-- 3. Verificar permissões nas tabelas
SELECT 
    table_name, 
    grantee, 
    string_agg(privilege_type, ', ') AS privileges
FROM 
    information_schema.table_privileges
WHERE 
    table_schema = 'public'
GROUP BY 
    table_name, grantee
ORDER BY 
    table_name, grantee;

-- 4. Verificar usuários e roles básicos
SELECT 
    rolname, 
    rolsuper
FROM 
    pg_roles
ORDER BY 
    rolname;

-- 5. Verificar especificamente as permissões da tabela 'divergencias'
SELECT 
    grantee, 
    privilege_type
FROM 
    information_schema.table_privileges
WHERE 
    table_schema = 'public' 
    AND table_name = 'divergencias'
ORDER BY 
    grantee, privilege_type;

-- 6. Verificar o owner de cada tabela
SELECT 
    tablename, 
    tableowner
FROM 
    pg_tables
WHERE 
    schemaname = 'public'
ORDER BY 
    tablename; 
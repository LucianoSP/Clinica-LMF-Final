-- Script simplificado para resolver problemas de permissão no Supabase
-- Este é o script mais simples possível, sem detecção de erros complexa

-- 1. Desabilitar RLS para todas as tabelas
DO $$
BEGIN
    -- Tabelas mais importantes do sistema
    ALTER TABLE planos_saude DISABLE ROW LEVEL SECURITY;
    ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;
    ALTER TABLE pacientes DISABLE ROW LEVEL SECURITY;
    ALTER TABLE especialidades DISABLE ROW LEVEL SECURITY;
    ALTER TABLE procedimentos DISABLE ROW LEVEL SECURITY;
    ALTER TABLE carteirinhas DISABLE ROW LEVEL SECURITY;
    ALTER TABLE guias DISABLE ROW LEVEL SECURITY;
    ALTER TABLE fichas DISABLE ROW LEVEL SECURITY;
    ALTER TABLE sessoes DISABLE ROW LEVEL SECURITY;
    ALTER TABLE execucoes DISABLE ROW LEVEL SECURITY;
    ALTER TABLE divergencias DISABLE ROW LEVEL SECURITY;
    ALTER TABLE agendamentos DISABLE ROW LEVEL SECURITY;
    ALTER TABLE storage DISABLE ROW LEVEL SECURITY;
    ALTER TABLE atendimentos_faturamento DISABLE ROW LEVEL SECURITY;
    -- Tabelas da nova integração
    ALTER TABLE processing_status DISABLE ROW LEVEL SECURITY;
    ALTER TABLE guias_queue DISABLE ROW LEVEL SECURITY;
    ALTER TABLE unimed_sessoes_capturadas DISABLE ROW LEVEL SECURITY;
    ALTER TABLE unimed_log_processamento DISABLE ROW LEVEL SECURITY;
    ALTER TABLE controle_importacao_pacientes DISABLE ROW LEVEL SECURITY;

    ALTER TABLE controle_importacao_agendamentos DISABLE ROW LEVEL SECURITY;
    ALTER TABLE mapeamento_ids_pacientes DISABLE ROW LEVEL SECURITY;
    ALTER TABLE mapeamento_ids_salas DISABLE ROW LEVEL SECURITY;
    ALTER TABLE mapeamento_ids_especialidades DISABLE ROW LEVEL SECURITY;
    ALTER TABLE mapeamento_ids_locais DISABLE ROW LEVEL SECURITY;
    ALTER TABLE mapeamento_ids_pagamentos DISABLE ROW LEVEL SECURITY;
    ALTER TABLE fichas_pendentes DISABLE ROW LEVEL SECURITY;
    
    
    RAISE NOTICE 'RLS desabilitado para as principais tabelas';
END $$;

-- 2. Conceder permissões para os usuários
DO $$
BEGIN
    -- Permissões para tabelas principais
    GRANT ALL ON TABLE planos_saude TO authenticated, anon, service_role;
    GRANT ALL ON TABLE usuarios TO authenticated, anon, service_role;
    GRANT ALL ON TABLE pacientes TO authenticated, anon, service_role;
    GRANT ALL ON TABLE especialidades TO authenticated, anon, service_role;
    GRANT ALL ON TABLE procedimentos TO authenticated, anon, service_role;
    GRANT ALL ON TABLE carteirinhas TO authenticated, anon, service_role;
    GRANT ALL ON TABLE guias TO authenticated, anon, service_role;
    GRANT ALL ON TABLE fichas TO authenticated, anon, service_role;
    GRANT ALL ON TABLE sessoes TO authenticated, anon, service_role;
    GRANT ALL ON TABLE execucoes TO authenticated, anon, service_role;
    GRANT ALL ON TABLE divergencias TO authenticated, anon, service_role;
    GRANT ALL ON TABLE agendamentos TO authenticated, anon, service_role;
    GRANT ALL ON TABLE storage TO authenticated, anon, service_role;
    GRANT ALL ON TABLE atendimentos_faturamento TO authenticated, anon, service_role;
    -- Tabelas da nova integração
    GRANT ALL ON TABLE processing_status TO authenticated, anon, service_role;
    GRANT ALL ON TABLE guias_queue TO authenticated, anon, service_role;
    GRANT ALL ON TABLE unimed_sessoes_capturadas TO authenticated, anon, service_role;
    GRANT ALL ON TABLE unimed_log_processamento TO authenticated, anon, service_role;
    GRANT ALL ON TABLE controle_importacao_pacientes TO authenticated, anon, service_role;

    GRANT ALL ON TABLE controle_importacao_agendamentos TO authenticated, anon, service_role;
    GRANT ALL ON TABLE mapeamento_ids_pacientes TO authenticated, anon, service_role;
    GRANT ALL ON TABLE mapeamento_ids_salas TO authenticated, anon, service_role;
    GRANT ALL ON TABLE mapeamento_ids_especialidades TO authenticated, anon, service_role;
    GRANT ALL ON TABLE mapeamento_ids_locais TO authenticated, anon, service_role;
    GRANT ALL ON TABLE mapeamento_ids_pagamentos TO authenticated, anon, service_role;
    GRANT ALL ON TABLE fichas_pendentes TO authenticated, anon, service_role;
    
    
    -- Permissões para sequências e schema
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated, anon, service_role;
    GRANT USAGE ON SCHEMA public TO authenticated, anon, service_role;
    
    RAISE NOTICE 'Permissões concedidas para todos os usuários';
END $$;

-- 3. Verificar planos_saude especificamente
DO $$
DECLARE
    count_planos INTEGER;
BEGIN
    -- Verificar se há dados em planos_saude
    SELECT COUNT(*) INTO count_planos FROM planos_saude;
    
    RAISE NOTICE 'Contagem de registros em planos_saude: %', count_planos;
    
    IF count_planos > 0 THEN
        RAISE NOTICE 'Há dados na tabela planos_saude';
    ELSE
        RAISE NOTICE 'A tabela planos_saude está vazia';
    END IF;
END $$; 
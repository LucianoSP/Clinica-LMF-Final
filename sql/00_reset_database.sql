-- 1. Dropar views materializadas
DROP MATERIALIZED VIEW IF EXISTS mv_execucoes_recentes CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_execucoes CASCADE;

-- 2. Dropar tabelas na ordem correta (por causa das dependências), exceto 'usuarios'
DROP TABLE IF EXISTS auditoria_execucoes CASCADE;
DROP TABLE IF EXISTS divergencias CASCADE;
DROP TABLE IF EXISTS atendimentos_faturamento CASCADE;
DROP TABLE IF EXISTS execucoes CASCADE;
DROP TABLE IF EXISTS sessoes CASCADE;
DROP TABLE IF EXISTS fichas_pendentes CASCADE;
DROP TABLE IF EXISTS fichas CASCADE;
DROP TABLE IF EXISTS guias CASCADE;
DROP TABLE IF EXISTS agendamentos CASCADE;
DROP TABLE IF EXISTS usuarios_profissoes CASCADE;
DROP TABLE IF EXISTS carteirinhas CASCADE;
DROP TABLE IF EXISTS usuarios_especialidades CASCADE;
DROP TABLE IF EXISTS usuarios_aba CASCADE;
DROP TABLE IF EXISTS salas CASCADE;
DROP TABLE IF EXISTS locais CASCADE;
DROP TABLE IF EXISTS profissoes CASCADE;
DROP TABLE IF EXISTS controle_importacao_tabelas_auxiliares CASCADE;
DROP TABLE IF EXISTS controle_importacao_pacientes CASCADE;
DROP TABLE IF EXISTS controle_importacao_agendamentos CASCADE;
DROP TABLE IF EXISTS storage CASCADE;
DROP TABLE IF EXISTS pacientes CASCADE;
DROP TABLE IF EXISTS procedimentos CASCADE;
DROP TABLE IF EXISTS especialidades CASCADE;
DROP TABLE IF EXISTS planos_saude CASCADE;
DROP TABLE IF EXISTS tipo_pagamento CASCADE;

-- Tabelas relacionadas ao Unimed Scraping (se existirem)
DROP TABLE IF EXISTS unimed_log_processamento CASCADE;
DROP TABLE IF EXISTS unimed_sessoes_capturadas CASCADE;
DROP TABLE IF EXISTS guias_queue CASCADE;
DROP TABLE IF EXISTS processing_status CASCADE;

-- 3. Dropar tipos enumerados (CUIDADO: Isso pode afetar a tabela 'usuarios' se ela usar algum desses tipos)
-- DROP TYPE IF EXISTS tipo_usuario CASCADE; -- Comentado para preservar a coluna em 'usuarios'
DROP TYPE IF EXISTS status_registro CASCADE;
DROP TYPE IF EXISTS tipo_procedimento CASCADE;
DROP TYPE IF EXISTS status_carteirinha CASCADE;
DROP TYPE IF EXISTS status_guia CASCADE;
DROP TYPE IF EXISTS tipo_guia CASCADE;
DROP TYPE IF EXISTS status_ficha CASCADE;
DROP TYPE IF EXISTS status_sessao CASCADE;
DROP TYPE IF EXISTS status_biometria CASCADE;
DROP TYPE IF EXISTS tipo_divergencia CASCADE;
DROP TYPE IF EXISTS status_divergencia CASCADE;
DROP TYPE IF EXISTS status_agendamento CASCADE;
DROP TYPE IF EXISTS tipo_unidade CASCADE;

-- Resetar outras estruturas (policies, triggers, funções) pode ser desnecessário
-- se os scripts subsequentes recriarem tudo.
-- Comente/descomente conforme necessário.

-- Apaga todo o schema public e recria (MUITO DESTRUTIVO - Use com extremo cuidado)
/*
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'Schema padrão para a aplicação ClinicalMF';
*/

-- Apaga todas as sessões ativas (exceto a sua própria)
-- (CUIDADO: Requer privilégios de superusuário)
/*
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid <> pg_backend_pid()
AND datname = current_database();
*/

-- Remover policies específicas (Pode ser redundante se o script de segurança recria tudo)
/*
DO $$
DECLARE
  tbl_name TEXT;
  pol_name TEXT;
BEGIN
  FOR tbl_name IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'usuarios')
  LOOP
    FOR pol_name IN (SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = tbl_name)
    LOOP
      EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I;', pol_name, tbl_name);
    END LOOP;
  END LOOP;
END $$;
*/

-- Remover triggers específicos (Pode ser redundante se o script de triggers recria tudo)
/*
DO $$
DECLARE
  tbl_name TEXT;
  trg_name TEXT;
BEGIN
  FOR tbl_name IN (SELECT event_object_table FROM information_schema.triggers WHERE trigger_schema = 'public' AND event_object_table != 'usuarios')
  LOOP
    FOR trg_name IN (SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema = 'public' AND event_object_table = tbl_name)
    LOOP
      EXECUTE format('DROP TRIGGER IF EXISTS %I ON public.%I;', trg_name, tbl_name);
    END LOOP;
  END LOOP;
END $$;
*/

-- Remover funções específicas (Pode ser redundante se os scripts de funções recriam tudo)
/*
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS update_processing_status_timestamp();
-- Adicione outras funções aqui, exceto as usadas por triggers da tabela 'usuarios'
*/

-- Mensagem de aviso
DO $$ BEGIN
  RAISE NOTICE '********************************************************************';
  RAISE NOTICE '* SCRIPT DE RESET EXECUTADO - TABELAS (EXCETO USUARIOS) REMOVIDAS *';
  RAISE NOTICE '* Certifique-se de que os scripts subsequentes recriarão tudo. *';
  RAISE NOTICE '********************************************************************';
END $$;

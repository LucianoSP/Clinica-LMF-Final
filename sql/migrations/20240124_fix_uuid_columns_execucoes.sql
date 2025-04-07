-- Primeiro remove as views que dependem da tabela execucoes
DROP VIEW IF EXISTS vw_relatorio_execucoes;
DROP MATERIALIZED VIEW IF EXISTS mv_execucoes;
DROP MATERIALIZED VIEW IF EXISTS mv_execucoes_recentes;

-- Ajusta os tipos das colunas na tabela execucoes
ALTER TABLE execucoes
    ALTER COLUMN id SET DATA TYPE uuid USING id::uuid,
    ALTER COLUMN guia_id SET DATA TYPE uuid USING guia_id::uuid,
    ALTER COLUMN sessao_id SET DATA TYPE uuid USING sessao_id::uuid,
    ALTER COLUMN usuario_executante SET DATA TYPE uuid USING usuario_executante::uuid,
    ALTER COLUMN created_by SET DATA TYPE uuid USING created_by::uuid,
    ALTER COLUMN updated_by SET DATA TYPE uuid USING updated_by::uuid;

-- Atualiza os relacionamentos
ALTER TABLE execucoes 
    DROP CONSTRAINT IF EXISTS execucoes_guia_id_fkey,
    DROP CONSTRAINT IF EXISTS execucoes_sessao_id_fkey,
    DROP CONSTRAINT IF EXISTS execucoes_usuario_executante_fkey,
    DROP CONSTRAINT IF EXISTS execucoes_created_by_fkey,
    DROP CONSTRAINT IF EXISTS execucoes_updated_by_fkey;

ALTER TABLE execucoes
    ADD CONSTRAINT execucoes_guia_id_fkey FOREIGN KEY (guia_id) REFERENCES guias(id) ON DELETE CASCADE,
    ADD CONSTRAINT execucoes_sessao_id_fkey FOREIGN KEY (sessao_id) REFERENCES sessoes(id),
    ADD CONSTRAINT execucoes_usuario_executante_fkey FOREIGN KEY (usuario_executante) REFERENCES auth.users(id),
    ADD CONSTRAINT execucoes_created_by_fkey FOREIGN KEY (created_by) REFERENCES auth.users(id),
    ADD CONSTRAINT execucoes_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES auth.users(id);
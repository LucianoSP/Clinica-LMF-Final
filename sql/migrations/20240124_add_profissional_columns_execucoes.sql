-- Adiciona novas colunas relacionadas ao profissional na tabela execucoes
ALTER TABLE execucoes
    ADD COLUMN IF NOT EXISTS conselho_profissional text,
    ADD COLUMN IF NOT EXISTS numero_conselho text,
    ADD COLUMN IF NOT EXISTS uf_conselho text,
    ADD COLUMN IF NOT EXISTS codigo_cbo text,
    ADD COLUMN IF NOT EXISTS profissional_executante text;

-- Adiciona comentários nas colunas para documentação
COMMENT ON COLUMN execucoes.conselho_profissional IS 'Conselho profissional do executante (ex: CRM, CREFITO)';
COMMENT ON COLUMN execucoes.numero_conselho IS 'Número de registro no conselho profissional';
COMMENT ON COLUMN execucoes.uf_conselho IS 'UF do conselho profissional';
COMMENT ON COLUMN execucoes.codigo_cbo IS 'Código CBO (Classificação Brasileira de Ocupações) do profissional';
COMMENT ON COLUMN execucoes.profissional_executante IS 'Nome completo do profissional executante';

-- Atualiza a política de segurança RLS para incluir as novas colunas
DROP POLICY IF EXISTS policy_select_execucoes ON execucoes;
CREATE POLICY policy_select_execucoes ON execucoes
    FOR SELECT USING (deleted_at IS NULL);

DROP POLICY IF EXISTS "Usuários autenticados podem inserir execucoes" ON execucoes;
CREATE POLICY "Usuários autenticados podem inserir execucoes" ON execucoes
    FOR INSERT TO authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "Usuários autenticados podem atualizar execucoes" ON execucoes;
CREATE POLICY "Usuários autenticados podem atualizar execucoes" ON execucoes
    FOR UPDATE TO authenticated
    USING (deleted_at IS NULL)
    WITH CHECK (true);
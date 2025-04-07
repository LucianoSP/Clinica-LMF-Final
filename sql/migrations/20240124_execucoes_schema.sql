-- Atualiza o tipo status_biometria se ainda não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_biometria') THEN
        CREATE TYPE status_biometria AS ENUM ('nao_verificado', 'verificado', 'falha');
    END IF;
END$$;

-- Atualiza a tabela execucoes
CREATE TABLE IF NOT EXISTS execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    guia_id uuid REFERENCES guias(id) ON DELETE CASCADE,
    sessao_id uuid REFERENCES sessoes(id),
    data_execucao date NOT NULL,
    data_atendimento date,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
    numero_guia text NOT NULL,
    codigo_ficha text NOT NULL,
    codigo_ficha_temp boolean DEFAULT false,
    usuario_executante uuid REFERENCES auth.users(id),
    origem text DEFAULT 'manual',
    ip_origem text,
    ordem_execucao integer,
    status_biometria status_biometria DEFAULT 'nao_verificado',
    conselho_profissional text,
    numero_conselho text,
    uf_conselho text,
    codigo_cbo text,
    profissional_executante text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES auth.users(id),
    updated_by uuid REFERENCES auth.users(id)
);

-- Cria índices para melhorar a performance
CREATE INDEX IF NOT EXISTS idx_execucoes_guia ON execucoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_sessao ON execucoes(sessao_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_execucoes_numero_guia ON execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_execucoes_carteirinha ON execucoes(paciente_carteirinha);
CREATE INDEX IF NOT EXISTS idx_execucoes_codigo_ficha ON execucoes(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_execucoes_profissional ON execucoes(profissional_executante);
CREATE INDEX IF NOT EXISTS idx_execucoes_conselho ON execucoes(conselho_profissional, numero_conselho, uf_conselho);
CREATE INDEX IF NOT EXISTS idx_execucoes_status ON execucoes(status_biometria);
CREATE INDEX IF NOT EXISTS idx_execucoes_deleted_at ON execucoes(deleted_at);

-- Adiciona comentários para documentação
COMMENT ON TABLE execucoes IS 'Registros de execuções de procedimentos';
COMMENT ON COLUMN execucoes.id IS 'Identificador único da execução';
COMMENT ON COLUMN execucoes.guia_id IS 'Referência à guia associada';
COMMENT ON COLUMN execucoes.sessao_id IS 'Referência à sessão associada';
COMMENT ON COLUMN execucoes.data_execucao IS 'Data em que o procedimento foi executado';
COMMENT ON COLUMN execucoes.data_atendimento IS 'Data do atendimento (opcional)';
COMMENT ON COLUMN execucoes.paciente_nome IS 'Nome do paciente';
COMMENT ON COLUMN execucoes.paciente_carteirinha IS 'Número da carteirinha do paciente';
COMMENT ON COLUMN execucoes.numero_guia IS 'Número da guia';
COMMENT ON COLUMN execucoes.codigo_ficha IS 'Código da ficha';
COMMENT ON COLUMN execucoes.codigo_ficha_temp IS 'Indica se o código da ficha é temporário';
COMMENT ON COLUMN execucoes.usuario_executante IS 'Usuário que executou o procedimento';
COMMENT ON COLUMN execucoes.origem IS 'Origem da execução (manual, sistema, importação)';
COMMENT ON COLUMN execucoes.ip_origem IS 'IP de origem da execução';
COMMENT ON COLUMN execucoes.ordem_execucao IS 'Ordem da execução';
COMMENT ON COLUMN execucoes.status_biometria IS 'Status da verificação biométrica';
COMMENT ON COLUMN execucoes.conselho_profissional IS 'Conselho profissional do executante (ex: CRM, CREFITO)';
COMMENT ON COLUMN execucoes.numero_conselho IS 'Número de registro no conselho profissional';
COMMENT ON COLUMN execucoes.uf_conselho IS 'UF do conselho profissional';
COMMENT ON COLUMN execucoes.codigo_cbo IS 'Código CBO do profissional';
COMMENT ON COLUMN execucoes.profissional_executante IS 'Nome do profissional executante';

-- Habilita RLS para a tabela
ALTER TABLE execucoes ENABLE ROW LEVEL SECURITY;

-- Configura as políticas de segurança
CREATE POLICY "Usuários podem ver execuções não deletadas" ON execucoes
    FOR SELECT USING (deleted_at IS NULL);

CREATE POLICY "Usuários autenticados podem inserir execuções" ON execucoes
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Usuários autenticados podem atualizar execuções" ON execucoes
    FOR UPDATE TO authenticated
    USING (deleted_at IS NULL)
    WITH CHECK (true);
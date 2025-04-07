-- 1. Tabelas base (sem foreign keys) - Corrigindo a tabela usuarios com NULL nas referências circulares
CREATE TABLE IF NOT EXISTS usuarios (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id uuid UNIQUE,
    nome text NOT NULL,
    email text UNIQUE,
    tipo_usuario tipo_usuario DEFAULT 'operador'::tipo_usuario,
    ativo boolean DEFAULT true,
    ultimo_acesso timestamptz,
    permissoes jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id) NULL,
    updated_by uuid REFERENCES usuarios(id) NULL,
    crm character varying(15),
    telefone character varying(15),
    foto text
);

CREATE TABLE IF NOT EXISTS planos_saude (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_operadora character varying(20) UNIQUE,
    registro_ans character varying(20),
    nome character varying(255) NOT NULL,
    tipo_plano character varying(50),
    abrangencia character varying(50),
    observacoes text,
    ativo boolean DEFAULT true,
    dados_contrato jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz
);

CREATE TABLE IF NOT EXISTS especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    anexo text,
    status status_registro DEFAULT 'ativo'::status_registro,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    especialidade_id VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS procedimentos (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo character varying(20) NOT NULL UNIQUE,
    nome text NOT NULL,
    descricao text,
    tipo tipo_procedimento NOT NULL,
    valor decimal(10,2),
    valor_filme decimal(10,2),
    valor_operacional decimal(10,2),
    valor_total decimal(10,2),
    tempo_medio_execucao interval,
    requer_autorizacao boolean DEFAULT true,
    observacoes text,
    ativo boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz
);

CREATE TABLE IF NOT EXISTS pacientes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    cpf character varying(14),
    rg character varying(15),
    data_nascimento date,
    foto text,
    nome_responsavel text,
    nome_pai text,
    nome_mae text,
    sexo character varying(1),
    cep character varying(9),
    endereco text,
    numero integer,
    complemento character varying(32),
    bairro character varying(64),
    cidade text,
    cidade_id integer,
    estado character(2),
    forma_pagamento integer,
    valor_consulta decimal(11,2),
    profissional_id uuid REFERENCES usuarios(id),
    escola_nome text,
    escola_ano text,
    escola_professor text,
    escola_periodo text,
    escola_contato text,
    patologia_id integer,
    tem_supervisor boolean DEFAULT false,
    supervisor_id uuid REFERENCES usuarios(id),
    tem_avaliacao_luria boolean DEFAULT false,
    avaliacao_luria_data_inicio_treinamento date,
    avaliacao_luria_reforcadores text,
    avaliacao_luria_obs_comportamento text,
    numero_carteirinha character varying(50),
    cpf_responsavel character varying(14),
    crm_medico character varying(15),
    nome_medico text,
    pai_nao_declarado boolean DEFAULT false,
    telefone character varying(15),
    email text,
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    importado boolean DEFAULT false,
    id_origem INT,
    data_registro_origem timestamptz,
    data_atualizacao_origem timestamptz
);

CREATE TABLE IF NOT EXISTS carteirinhas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id uuid NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    plano_saude_id uuid NOT NULL REFERENCES planos_saude(id) ON DELETE RESTRICT,
    numero_carteirinha text NOT NULL,
    data_validade date,
    status status_carteirinha NOT NULL DEFAULT 'ativa',
    motivo_inativacao text,
    historico_status jsonb DEFAULT '[]',
    titular boolean DEFAULT false,
    nome_titular text,
    cpf_titular character varying(14),
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE(plano_saude_id, numero_carteirinha)
);

-- 3. Segunda camada
CREATE TABLE IF NOT EXISTS guias (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    carteirinha_id uuid NOT NULL REFERENCES carteirinhas(id) ON DELETE RESTRICT,
    paciente_id uuid NOT NULL REFERENCES pacientes(id),
    procedimento_id uuid NOT NULL REFERENCES procedimentos(id),
    numero_guia text NOT NULL,
    data_solicitacao date DEFAULT CURRENT_DATE,
    data_autorizacao date,
    status status_guia DEFAULT 'rascunho'::status_guia,
    tipo tipo_guia NOT NULL,
    quantidade_autorizada int,
    quantidade_executada int DEFAULT 0,
    motivo_negacao text,
    codigo_servico text,
    descricao_servico text,
    quantidade int DEFAULT 1,
    observacoes text,
    dados_autorizacao jsonb DEFAULT '{}'::jsonb,
    historico_status jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE(numero_guia)
);

-- 4. Terceira camada - Corrigindo a ordem de criação de tabelas (fichas agora está depois de agendamentos)
CREATE TABLE IF NOT EXISTS fichas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_ficha text NOT NULL,
    guia_id uuid REFERENCES guias(id),
    agendamento_id uuid REFERENCES agendamentos(id),
    numero_guia text NOT NULL,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
    arquivo_digitalizado text,
    storage_id uuid REFERENCES storage(id),
    status status_ficha DEFAULT 'pendente'::status_ficha,
    data_atendimento date NOT NULL,
    total_sessoes integer DEFAULT 1,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    UNIQUE(id, codigo_ficha),
    CONSTRAINT fk_guia_numero FOREIGN KEY (numero_guia) REFERENCES guias(numero_guia)
);

-- Adiciona um índice único parcial para garantir unicidade do codigo_ficha quando não excluído
CREATE UNIQUE INDEX IF NOT EXISTS idx_fichas_codigo_ficha_unique 
ON fichas (codigo_ficha) 
WHERE deleted_at IS NULL;

-- 5. Quarta camada
CREATE TABLE IF NOT EXISTS sessoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    ficha_id uuid REFERENCES fichas(id) ON DELETE CASCADE,
    guia_id uuid REFERENCES guias(id),
    data_sessao date NOT NULL,
    possui_assinatura boolean DEFAULT false,
    procedimento_id uuid REFERENCES procedimentos(id),
    profissional_executante text,
    status status_sessao DEFAULT 'pendente',
    numero_guia text NOT NULL,
    codigo_ficha text NOT NULL,
    origem text DEFAULT 'manual',
    ip_origem inet,
    ordem_execucao integer,
    status_biometria status_biometria DEFAULT 'nao_verificado',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    CONSTRAINT fk_ficha_codigo FOREIGN KEY (ficha_id, codigo_ficha) REFERENCES fichas(id, codigo_ficha)
);

-- 6. Quinta camada
CREATE TABLE IF NOT EXISTS execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    guia_id uuid REFERENCES guias(id) ON DELETE CASCADE,
    sessao_id uuid REFERENCES sessoes(id) ON DELETE CASCADE,
    data_execucao date NOT NULL,
    data_atendimento date,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
    numero_guia text NOT NULL,
    codigo_ficha text NOT NULL,
    codigo_ficha_temp boolean DEFAULT false,
    usuario_executante uuid REFERENCES usuarios(id),
    origem text DEFAULT 'manual',
    ip_origem inet,
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
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    CONSTRAINT fk_execucoes_guia_numero FOREIGN KEY (numero_guia) REFERENCES guias(numero_guia)
);




- Script unificado para criação do schema completo
-- Função para gerar UUIDs (necessário para alguns bancos)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Tabela para controle do status do processamento
CREATE TABLE IF NOT EXISTS processing_status (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id text UNIQUE NOT NULL,
    status text DEFAULT 'pending',
    total_guides integer DEFAULT 0,
    processed_guides integer DEFAULT 0,
    error text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    completed_at timestamptz,
    start_date text,
    end_date text,
    max_guides integer,
    retry_guides integer DEFAULT 0,
    started_at timestamptz DEFAULT now(),
    error_at timestamptz,
    last_update timestamptz,
    total_execucoes INTEGER,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'iniciado', 'capturing', 'processing', 'finalizado', 'completed', 'completed_with_errors', 'error'))
);

-- Tabela temporária para fila de processamento de guias
CREATE TABLE IF NOT EXISTS guias_queue (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL,
    data_atendimento_completa text NOT NULL, -- Formato dd/mm/aaaa hh:mm
    status text DEFAULT 'pending',
    task_id text REFERENCES processing_status(task_id),
    attempts integer DEFAULT 0,
    error text,
    processed_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(numero_guia, data_atendimento_completa),
    CONSTRAINT valid_queue_status CHECK (status IN ('pending', 'processado', 'erro', 'falha_permanente'))
);

-- Tabela para armazenar dados da sessão capturada da Unimed
CREATE TABLE IF NOT EXISTS unimed_sessoes_capturadas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL,
    data_atendimento_completa text NOT NULL, -- Formato dd/mm/aaaa hh:mm
    data_execucao date,
    paciente_nome text,
    paciente_carteirinha text,
    codigo_ficha text,
    profissional_executante text,
    conselho_profissional text,
    numero_conselho text,
    uf_conselho text,
    codigo_cbo text,
    origem text DEFAULT 'unimed_scraping',
    status text DEFAULT 'pendente',
    error text,
    task_id text REFERENCES processing_status(task_id),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    processed_at timestamptz,
    UNIQUE(numero_guia, data_atendimento_completa),
    CONSTRAINT valid_unimed_status CHECK (status IN ('pendente', 'processado', 'erro'))
);

-- Tabela para log de processamento das sessões da Unimed
CREATE TABLE IF NOT EXISTS unimed_log_processamento (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    sessao_id uuid REFERENCES unimed_sessoes_capturadas(id) ON DELETE CASCADE,
    execucao_id uuid REFERENCES execucoes(id),
    status text NOT NULL,
    mensagem text,
    detalhes jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Função para atualizar o timestamp last_update na tabela processing_status
CREATE OR REPLACE FUNCTION update_processing_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar timestamps
CREATE TRIGGER set_processing_status_timestamp
    BEFORE UPDATE ON processing_status
    FOR EACH ROW
    EXECUTE PROCEDURE update_processing_status_timestamp();

CREATE TRIGGER update_guias_queue_updated_at
    BEFORE UPDATE ON guias_queue
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_execucoes_updated_at
    BEFORE UPDATE ON execucoes
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_unimed_sessoes_updated_at
    BEFORE UPDATE ON unimed_sessoes_capturadas
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_unimed_log_updated_at
    BEFORE UPDATE ON unimed_log_processamento
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Índices para otimização de consultas - Guias Queue
CREATE INDEX IF NOT EXISTS idx_guias_queue_status ON guias_queue(status);
CREATE INDEX IF NOT EXISTS idx_guias_queue_task_id ON guias_queue(task_id);
CREATE INDEX IF NOT EXISTS idx_guias_queue_attempts ON guias_queue(attempts);

-- Índices para processing status
CREATE INDEX IF NOT EXISTS idx_processing_status_task_id ON processing_status(task_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_status ON processing_status(status);
CREATE INDEX IF NOT EXISTS idx_processing_status_dates ON processing_status(started_at, error_at, last_update);

-- Índices para execuções
CREATE INDEX IF NOT EXISTS idx_execucoes_numero_guia ON execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_execucoes_codigo_ficha ON execucoes(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_atendimento, data_execucao);
CREATE INDEX IF NOT EXISTS idx_execucoes_ordem ON execucoes(ordem_execucao);

-- Índices para tabelas de Unimed
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_numero_guia ON unimed_sessoes_capturadas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_status ON unimed_sessoes_capturadas(status);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_datas ON unimed_sessoes_capturadas(data_execucao, processed_at);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_task_id ON unimed_sessoes_capturadas(task_id);
CREATE INDEX IF NOT EXISTS idx_unimed_log_status ON unimed_log_processamento(status);
CREATE INDEX IF NOT EXISTS idx_unimed_log_sessao ON unimed_log_processamento(sessao_id);
CREATE INDEX IF NOT EXISTS idx_unimed_log_execucao ON unimed_log_processamento(execucao_id);

-- Função para incrementar guias processadas
CREATE OR REPLACE FUNCTION increment_processed_guides(inc integer)
RETURNS void AS $$
BEGIN
  UPDATE processing_status
  SET processed_guides = COALESCE(processed_guides, 0) + inc
  WHERE status NOT IN ('completed', 'error', 'finalizado')
  AND updated_at >= NOW() - INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- Função para inserir dados na tabela execucoes a partir das sessões capturadas da Unimed
CREATE OR REPLACE FUNCTION inserir_execucao_unimed(sessao_id uuid)
RETURNS uuid AS $$
DECLARE
    nova_execucao_id uuid;
    guia_id uuid;
    sessao_rec RECORD;
BEGIN
    -- Busca dados da sessão
    SELECT * INTO sessao_rec FROM unimed_sessoes_capturadas WHERE id = sessao_id;
    
    -- Busca guia_id
    SELECT id INTO guia_id FROM guias WHERE numero_guia = sessao_rec.numero_guia LIMIT 1;
    
    -- Se não encontrou guia, retorna NULL
    IF guia_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Insere na tabela execucoes
    INSERT INTO execucoes (
        guia_id,
        data_execucao,
        data_atendimento,
        paciente_nome,
        paciente_carteirinha,
        numero_guia,
        codigo_ficha,
        origem,
        profissional_executante,
        conselho_profissional,
        numero_conselho,
        uf_conselho,
        codigo_cbo
    ) VALUES (
        guia_id,
        sessao_rec.data_execucao,
        sessao_rec.data_execucao, -- Usando a mesma data como data_atendimento
        sessao_rec.paciente_nome,
        sessao_rec.paciente_carteirinha,
        sessao_rec.numero_guia,
        sessao_rec.codigo_ficha,
        'unimed_scraping',
        sessao_rec.profissional_executante,
        sessao_rec.conselho_profissional,
        sessao_rec.numero_conselho,
        sessao_rec.uf_conselho,
        sessao_rec.codigo_cbo
    )
    RETURNING id INTO nova_execucao_id;
    
    -- Atualiza o status da sessão
    UPDATE unimed_sessoes_capturadas 
    SET 
        status = 'processado',
        processed_at = now()
    WHERE id = sessao_id;
    
    -- Registra log
    INSERT INTO unimed_log_processamento (
        sessao_id,
        execucao_id,
        status,
        mensagem
    ) VALUES (
        sessao_id,
        nova_execucao_id,
        'sucesso',
        'Execução inserida com sucesso'
    );
    
    RETURN nova_execucao_id;
EXCEPTION WHEN OTHERS THEN
    -- Em caso de erro, registra o log
    INSERT INTO unimed_log_processamento (
        sessao_id,
        status,
        mensagem,
        detalhes
    ) VALUES (
        sessao_id,
        'erro',
        'Erro ao inserir execução: ' || SQLERRM,
        jsonb_build_object('error', SQLERRM, 'state', SQLSTATE)
    );
    
    -- Atualiza o status da sessão
    UPDATE unimed_sessoes_capturadas 
    SET 
        status = 'erro',
        error = SQLERRM
    WHERE id = sessao_id;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql; 
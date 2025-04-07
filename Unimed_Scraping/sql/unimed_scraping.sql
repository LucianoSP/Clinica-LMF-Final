-- Script unificado para criação do schema completo
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
    ordem_execucao INTEGER NULL,
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

--================ FUNÇÕES ESPECÍFICAS DO SCRAPING =================

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

-- Função para inserir dados na tabela execucoes a partir das sessões capturadas da Unimed (Refatorada - Fase 1 Plano)
CREATE OR REPLACE FUNCTION inserir_execucao_unimed(p_sessao_id uuid)
RETURNS uuid AS $$
DECLARE
    nova_execucao_id uuid;
    guia_id_encontrada uuid;
    sessao_id_encontrada uuid;
    sessao_rec RECORD;
    v_log_mensagem TEXT;
    v_log_status TEXT := 'sucesso';
    v_link_manual BOOLEAN := FALSE;
    v_codigo_ficha TEXT;
    v_codigo_ficha_temp BOOLEAN := TRUE;
    v_count INTEGER;
    v_paciente_id uuid;
    v_agendamento_id uuid;
BEGIN
    -- Busca dados da sessão capturada
    SELECT usc.*, g.paciente_id as guia_paciente_id
    INTO sessao_rec
    FROM unimed_sessoes_capturadas usc
    LEFT JOIN guias g ON usc.numero_guia = g.numero_guia -- Junta com guias para pegar paciente_id
    WHERE usc.id = p_sessao_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sessão unimed_sessoes_capturadas com ID % não encontrada', p_sessao_id;
    END IF;
    
    v_paciente_id := sessao_rec.guia_paciente_id; -- Usa o paciente_id da guia

    -- Busca guia_id na tabela guias
    SELECT id INTO guia_id_encontrada FROM guias WHERE numero_guia = sessao_rec.numero_guia LIMIT 1;

    -- Se não encontrou guia no sistema principal, loga erro e sai
    IF guia_id_encontrada IS NULL THEN
        v_log_status := 'erro';
        v_log_mensagem := 'Erro: Guia ' || sessao_rec.numero_guia || ' não encontrada na tabela principal guias.';
        INSERT INTO unimed_log_processamento (sessao_id, status, mensagem) VALUES (p_sessao_id, v_log_status, v_log_mensagem);
        UPDATE unimed_sessoes_capturadas SET status = 'erro', error = v_log_mensagem, processed_at = now() WHERE id = p_sessao_id;
        RETURN NULL;
    END IF;

    -- Tenta encontrar a SESSAO correspondente com base nos critérios
    sessao_id_encontrada := NULL;

    -- Busca Primária (Alta Confiança): Guia + Data Exata + Ordem Exata (se disponível)
    IF sessao_rec.ordem_execucao IS NOT NULL THEN
        SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id -- Tenta pegar agendamento_id da sessão
        FROM sessoes s
        WHERE s.numero_guia = sessao_rec.numero_guia
          AND s.data_sessao = sessao_rec.data_execucao
          AND s.ordem_execucao = sessao_rec.ordem_execucao
          AND s.deleted_at IS NULL
        LIMIT 1;
    ELSE -- Se ordem não veio do scraping, busca só por guia e data
        SELECT count(*) INTO v_count -- Verifica ambiguidade primeiro
        FROM sessoes s
        WHERE s.numero_guia = sessao_rec.numero_guia
          AND s.data_sessao = sessao_rec.data_execucao
          AND s.ordem_execucao IS NULL
          AND s.deleted_at IS NULL;

        IF v_count = 1 THEN -- Só busca se for única
            SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND s.data_sessao = sessao_rec.data_execucao
              AND s.ordem_execucao IS NULL -- Considera apenas sessões sem ordem definida tbm
              AND s.deleted_at IS NULL
            LIMIT 1;
        ELSIF v_count > 1 THEN
            v_link_manual := TRUE;
            v_log_mensagem := 'Vinculação Exata falhou: Ambiguidade (múltiplas sessões sem ordem na mesma data/guia).';
        END IF;
    END IF;

    IF sessao_id_encontrada IS NOT NULL THEN
        v_log_mensagem := 'Vinculado por critério Exato (Guia+Data[+Ordem]).';
    ELSE
        -- Busca Secundária (Tolerância + Ordem - se disponível): Guia + Data +/- 1 dia + Ordem Exata
        IF sessao_rec.ordem_execucao IS NOT NULL THEN
            -- Verifica quantas candidatas existem na janela
            SELECT count(*) INTO v_count
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
              AND s.ordem_execucao = sessao_rec.ordem_execucao
              AND s.deleted_at IS NULL;

            IF v_count = 1 THEN -- Só vincula se for única
                SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
                FROM sessoes s
                WHERE s.numero_guia = sessao_rec.numero_guia
                  AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
                  AND s.ordem_execucao = sessao_rec.ordem_execucao
                  AND s.deleted_at IS NULL
                ORDER BY abs(s.data_sessao - sessao_rec.data_execucao) -- Pega a mais próxima (já que é única)
                LIMIT 1;
                v_log_mensagem := 'Vinculado por Tolerância+Ordem (Guia+Data+/-1d+Ordem).';
            ELSIF v_count > 1 THEN
               v_link_manual := TRUE;
               v_log_mensagem := 'Vinculação Tolerância+Ordem falhou: Ambiguidade (múltiplas sessões com mesma ordem na janela de data).';
            END IF;
        END IF;

        -- Busca Terciária (Tolerância sem Ordem - Cuidado!): Guia + Data +/- 1 dia (Só se ÚNICA)
        IF sessao_id_encontrada IS NULL THEN
            SELECT count(*) INTO v_count
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
              AND s.deleted_at IS NULL;

            IF v_count = 1 THEN -- Só vincula se encontrou EXATAMENTE uma
                SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
                FROM sessoes s
                WHERE s.numero_guia = sessao_rec.numero_guia
                  AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
                  AND s.deleted_at IS NULL
                LIMIT 1;
                v_log_mensagem := 'Vinculado por Tolerância s/ Ordem (Única sessão na janela Guia+Data+/-1d).';
            ELSE
                -- Se v_count = 0 ou v_count > 1, não vincula e marca para revisão manual
                v_link_manual := TRUE;
                IF v_count = 0 THEN
                    v_log_mensagem := 'Vinculação falhou: Nenhuma sessão encontrada na janela Guia+Data+/-1d.';
                ELSE
                    v_log_mensagem := 'Vinculação falhou: Ambiguidade (múltiplas sessões encontradas na janela Guia+Data+/-1d sem ordem).';
                END IF;
            END IF;
        END IF;
    END IF;

    -- Define codigo_ficha e codigo_ficha_temp baseado na vinculação
    IF sessao_id_encontrada IS NOT NULL THEN
        SELECT codigo_ficha INTO v_codigo_ficha FROM sessoes WHERE id = sessao_id_encontrada;
        v_codigo_ficha_temp := FALSE; -- Vinculação bem sucedida
    ELSE
        v_codigo_ficha := sessao_rec.codigo_ficha; -- Usa o código temporário do scraping
        v_codigo_ficha_temp := TRUE;
        -- Se não vinculou a sessão, tenta buscar agendamento pelo paciente/data
        IF v_paciente_id IS NOT NULL AND sessao_rec.data_execucao IS NOT NULL THEN
             SELECT count(*) INTO v_count
             FROM agendamentos a
             WHERE a.paciente_id = v_paciente_id
               AND abs(a.data_agendamento - sessao_rec.data_execucao) <= 1; -- Tolerância de 1 dia

             IF v_count = 1 THEN -- Vincula agendamento se único
                 SELECT a.id INTO v_agendamento_id
                 FROM agendamentos a
                 WHERE a.paciente_id = v_paciente_id
                   AND abs(a.data_agendamento - sessao_rec.data_execucao) <= 1
                 LIMIT 1;
             END IF;
        END IF;
    END IF;

    -- Insere na tabela execucoes
    INSERT INTO execucoes (
        guia_id,
        sessao_id, -- Pode ser NULL se não vinculou
        agendamento_id, -- Preenche se encontrou
        paciente_id,
        data_execucao,
        data_atendimento, -- Usando a mesma data como data_atendimento por enquanto
        paciente_nome,
        paciente_carteirinha,
        numero_guia,
        codigo_ficha,
        codigo_ficha_temp,
        origem,
        profissional_executante,
        conselho_profissional,
        numero_conselho,
        uf_conselho,
        codigo_cbo,
        ordem_execucao,         -- Campo novo
        link_manual_necessario -- Campo novo
    ) VALUES (
        guia_id_encontrada,
        sessao_id_encontrada,
        v_agendamento_id,
        v_paciente_id,
        sessao_rec.data_execucao,
        sessao_rec.data_execucao,
        sessao_rec.paciente_nome,
        sessao_rec.paciente_carteirinha,
        sessao_rec.numero_guia,
        v_codigo_ficha,
        v_codigo_ficha_temp,
        'unimed_scraping',
        sessao_rec.profissional_executante,
        sessao_rec.conselho_profissional,
        sessao_rec.numero_conselho,
        sessao_rec.uf_conselho,
        sessao_rec.codigo_cbo,
        sessao_rec.ordem_execucao,
        v_link_manual
    )
    RETURNING id INTO nova_execucao_id;

    -- Atualiza o status da sessão capturada
    UPDATE unimed_sessoes_capturadas
    SET
        status = 'processado',
        processed_at = now()
    WHERE id = p_sessao_id;

    -- Registra log detalhado
    INSERT INTO unimed_log_processamento (
        sessao_id,
        execucao_id,
        status,
        mensagem,
        detalhes
    ) VALUES (
        p_sessao_id,
        nova_execucao_id,
        v_log_status, -- Será 'sucesso' se não houve erro de guia
        v_log_mensagem, -- Mensagem sobre a vinculação
        jsonb_build_object(
            'sessao_vinculada_id', sessao_id_encontrada,
            'agendamento_vinculado_id', v_agendamento_id,
            'link_manual_necessario', v_link_manual,
            'codigo_ficha_usado', v_codigo_ficha,
            'codigo_ficha_era_temp', v_codigo_ficha_temp
        )
    );

    RETURN nova_execucao_id;

EXCEPTION WHEN OTHERS THEN
    -- Em caso de erro inesperado, registra o log de erro
    v_log_status := 'erro';
    v_log_mensagem := 'Erro inesperado ao processar/inserir execução: ' || SQLERRM || ' | State: ' || SQLSTATE;
    INSERT INTO unimed_log_processamento (
        sessao_id,
        status,
        mensagem,
        detalhes
    ) VALUES (
        p_sessao_id,
        v_log_status,
        v_log_mensagem,
        jsonb_build_object('error', SQLERRM, 'state', SQLSTATE)
    );

    -- Atualiza o status da sessão capturada para erro
    UPDATE unimed_sessoes_capturadas
    SET
        status = 'erro',
        error = SQLERRM,
        processed_at = now()
    WHERE id = p_sessao_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql; 
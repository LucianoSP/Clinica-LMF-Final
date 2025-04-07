-- Tabela para armazenar fichas pendentes que não puderam ser inseridas normalmente
-- devido a problemas de integridade referencial (como guias inexistentes)

CREATE TABLE IF NOT EXISTS fichas_pendentes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    storage_id uuid REFERENCES storage(id),
    dados_extraidos jsonb NOT NULL,
    status text DEFAULT 'pendente',
    arquivo_url text,
    numero_guia text,
    paciente_nome text,
    paciente_carteirinha text,
    data_atendimento date,
    total_sessoes integer,
    codigo_ficha text,
    observacoes text,
    processado boolean DEFAULT false,
    data_processamento timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id)
);

COMMENT ON TABLE fichas_pendentes IS 'Armazena temporariamente fichas que não puderam ser inseridas diretamente na tabela fichas devido a restrições de chave estrangeira';

-- Função para inserir ficha ignorando a restrição de chave estrangeira
-- Esta função deve ser usada com cuidado, pois pode criar inconsistências no banco de dados
CREATE OR REPLACE FUNCTION public.inserir_ficha_bypass_fk(
    p_dados_ficha jsonb,
    p_storage_id uuid,
    p_ignorar_fk boolean DEFAULT false
) RETURNS uuid AS $$
DECLARE
    v_ficha_id uuid;
    v_numero_guia text;
    v_guia_id uuid;
BEGIN
    -- Se p_ignorar_fk for true, tenta criar uma guia temporária
    IF p_ignorar_fk THEN
        v_numero_guia := p_dados_ficha->>'numero_guia';
        
        -- Se a guia não existir, cria uma registro temporário
        IF v_numero_guia IS NOT NULL THEN
            -- Verifica se a guia já existe
            SELECT id INTO v_guia_id FROM guias WHERE numero_guia = v_numero_guia;
            
            IF v_guia_id IS NULL THEN
                -- Primeiro registra a ficha em fichas_pendentes para processamento posterior
                INSERT INTO fichas_pendentes (
                    storage_id,
                    dados_extraidos,
                    status,
                    arquivo_url,
                    numero_guia,
                    paciente_nome,
                    paciente_carteirinha,
                    data_atendimento,
                    total_sessoes,
                    codigo_ficha,
                    observacoes
                ) VALUES (
                    p_storage_id,
                    p_dados_ficha,
                    'pendente',
                    p_dados_ficha->>'arquivo_digitalizado',
                    v_numero_guia,
                    p_dados_ficha->>'paciente_nome',
                    p_dados_ficha->>'paciente_carteirinha',
                    (p_dados_ficha->>'data_atendimento')::date,
                    (p_dados_ficha->>'total_sessoes')::integer,
                    p_dados_ficha->>'codigo_ficha',
                    'Ficha pendente de processamento manual - guia não encontrada'
                )
                RETURNING id INTO v_ficha_id;
                
                RETURN v_ficha_id;
            END IF;
        END IF;
    END IF;
    
    -- Se não tiver que ignorar FK ou se a guia existir, insere normalmente
    INSERT INTO fichas (
        storage_id,
        codigo_ficha,
        numero_guia,
        paciente_nome,
        paciente_carteirinha,
        arquivo_digitalizado,
        status,
        data_atendimento,
        total_sessoes
    ) VALUES (
        p_storage_id,
        p_dados_ficha->>'codigo_ficha',
        p_dados_ficha->>'numero_guia',
        p_dados_ficha->>'paciente_nome',
        p_dados_ficha->>'paciente_carteirinha',
        p_dados_ficha->>'arquivo_digitalizado',
        'pendente',
        (p_dados_ficha->>'data_atendimento')::date,
        (p_dados_ficha->>'total_sessoes')::integer
    )
    RETURNING id INTO v_ficha_id;
    
    RETURN v_ficha_id;
EXCEPTION
    WHEN OTHERS THEN
        -- Em caso de erro, salva na tabela de pendentes
        INSERT INTO fichas_pendentes (
            storage_id,
            dados_extraidos,
            status,
            arquivo_url,
            numero_guia,
            paciente_nome,
            paciente_carteirinha,
            data_atendimento,
            total_sessoes,
            codigo_ficha,
            observacoes
        ) VALUES (
            p_storage_id,
            p_dados_ficha,
            'erro',
            p_dados_ficha->>'arquivo_digitalizado',
            p_dados_ficha->>'numero_guia',
            p_dados_ficha->>'paciente_nome',
            p_dados_ficha->>'paciente_carteirinha',
            (p_dados_ficha->>'data_atendimento')::date,
            (p_dados_ficha->>'total_sessoes')::integer,
            p_dados_ficha->>'codigo_ficha',
            'Erro ao processar: ' || SQLERRM
        )
        RETURNING id INTO v_ficha_id;
        
        RETURN v_ficha_id;
END;
$$ LANGUAGE plpgsql; 
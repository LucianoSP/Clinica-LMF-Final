--================ FUNÇÕES AUXILIARES =================

-- Função para atualizar updated_at automaticamente (definida uma única vez)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Função para atualizar o timestamp last_update na tabela processing_status
CREATE OR REPLACE FUNCTION update_processing_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Função para enriquecer agendamentos com dados de relacionamentos (Considerar mover para funções de negócio se ficar complexa)
CREATE OR REPLACE FUNCTION proc_agendamento_enriquecer_dados()
RETURNS TRIGGER AS $$
DECLARE
    v_paciente_id UUID;
    v_paciente_nome TEXT;
    v_carteirinha TEXT;
    v_procedimento_nome TEXT;
BEGIN
    -- Verificar se temos um paciente_id
    IF NEW.paciente_id IS NOT NULL THEN
        -- Buscar nome do paciente
        SELECT nome INTO v_paciente_nome
        FROM pacientes
        WHERE id = NEW.paciente_id;
        
        -- Buscar carteirinha do paciente (primeira encontrada)
        SELECT numero_carteirinha INTO v_carteirinha
        FROM carteirinhas
        WHERE paciente_id = NEW.paciente_id
        LIMIT 1;
    END IF;
    
    -- Verificar se temos um procedimento_id
    IF NEW.procedimento_id IS NOT NULL THEN
        -- Buscar nome do procedimento
        SELECT nome INTO v_procedimento_nome
        FROM procedimentos
        WHERE id = NEW.procedimento_id;
    END IF;
    
    -- Adicionar o resultado como campos virtuais (sem armazenar na tabela)
    -- Nota: Campos virtuais não são padrão SQL, isso é mais uma lógica de trigger.
    -- Se a intenção é exibir esses dados, uma VIEW (vw_agendamentos_completos) é mais apropriada.
    -- Removendo a atribuição a campos virtuais que não existem:
    -- NEW.paciente_nome_virtual := v_paciente_nome;
    -- NEW.carteirinha_virtual := v_carteirinha;
    -- NEW.procedimento_nome_virtual := v_procedimento_nome;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
COMMENT ON FUNCTION proc_agendamento_enriquecer_dados() IS 'Trigger atualmente não utilizado para enriquecer agendamentos. Usar VIEW vw_agendamentos_completos.';

-- Função para limpar dados na importação
CREATE OR REPLACE FUNCTION fn_limpar_dados_importacao_agendamentos(dados JSONB)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    -- Criar uma cópia dos dados, removendo campos que não existem na tabela
    result := dados - 'carteirinha' - 'paciente_nome' - 'cod_paciente' - 'pagamento' - 'sala' - 
              'id_profissional' - 'profissional' - 'tipo_atend' - 'qtd_sess' - 'elegibilidade' - 
              'substituicao' - 'tipo_falta' - 'id_pai' - 'codigo_faturamento' - 'id_atendimento';
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
COMMENT ON FUNCTION fn_limpar_dados_importacao_agendamentos(JSONB) IS 'Função para limpar dados redundantes na importação de agendamentos'; 
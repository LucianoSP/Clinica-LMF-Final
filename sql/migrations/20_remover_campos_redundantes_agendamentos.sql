-- Migração para atualizar o esquema de agendamentos no PostgreSQL
-- Objetivo: Remover campos redundantes e garantir compatibilidade com o modelo de relacionamentos

-- Criar uma trigger que adiciona dados de pacientes de forma dinâmica
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
    NEW.paciente_nome_virtual := v_paciente_nome;
    NEW.carteirinha_virtual := v_carteirinha;
    NEW.procedimento_nome_virtual := v_procedimento_nome;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

-- Comentários para documentação
COMMENT ON FUNCTION proc_agendamento_enriquecer_dados() IS 'Trigger para enriquecer agendamentos com dados de pacientes e procedimentos através de relacionamentos';
COMMENT ON FUNCTION fn_limpar_dados_importacao_agendamentos(JSONB) IS 'Função para limpar dados redundantes na importação de agendamentos';

-- Criar Views para simplificar consultas
CREATE OR REPLACE VIEW vw_agendamentos_completos AS
SELECT 
    a.*,
    p.nome AS paciente_nome,
    c.numero_carteirinha AS carteirinha,
    proc.nome AS procedimento_nome
FROM 
    agendamentos a
LEFT JOIN 
    pacientes p ON a.paciente_id = p.id
LEFT JOIN 
    carteirinhas c ON p.id = c.paciente_id
LEFT JOIN 
    procedimentos proc ON a.procedimento_id = proc.id;

COMMENT ON VIEW vw_agendamentos_completos IS 'Visão que inclui dados completos de agendamentos com informações de pacientes e procedimentos'; 
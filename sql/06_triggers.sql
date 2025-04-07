--================ TRIGGERS =================

-- Triggers para atualização automática de updated_at em tabelas base e relacionamentos
DROP TRIGGER IF EXISTS update_usuarios_updated_at ON usuarios;
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_planos_saude_updated_at ON planos_saude;
CREATE TRIGGER update_planos_saude_updated_at BEFORE UPDATE ON planos_saude FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_especialidades_updated_at ON especialidades;
CREATE TRIGGER update_especialidades_updated_at BEFORE UPDATE ON especialidades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_procedimentos_updated_at ON procedimentos;
CREATE TRIGGER update_procedimentos_updated_at BEFORE UPDATE ON procedimentos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pacientes_updated_at ON pacientes;
CREATE TRIGGER update_pacientes_updated_at BEFORE UPDATE ON pacientes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_storage_updated_at ON storage;
CREATE TRIGGER update_storage_updated_at BEFORE UPDATE ON storage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_controle_importacao_agendamentos_updated_at ON controle_importacao_agendamentos;
CREATE TRIGGER update_controle_importacao_agendamentos_updated_at BEFORE UPDATE ON controle_importacao_agendamentos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_controle_importacao_pacientes_updated_at ON controle_importacao_pacientes;
CREATE TRIGGER update_controle_importacao_pacientes_updated_at BEFORE UPDATE ON controle_importacao_pacientes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- REMOVIDO: Trigger para controle_importacao_tabelas_auxiliares pois não possui coluna updated_at
DROP TRIGGER IF EXISTS update_controle_importacao_tabelas_auxiliares_updated_at ON controle_importacao_tabelas_auxiliares;
-- CREATE TRIGGER update_controle_importacao_tabelas_auxiliares_updated_at BEFORE UPDATE ON controle_importacao_tabelas_auxiliares FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_profissoes_updated_at ON profissoes;
CREATE TRIGGER update_profissoes_updated_at BEFORE UPDATE ON profissoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_locais_updated_at ON locais;
CREATE TRIGGER update_locais_updated_at BEFORE UPDATE ON locais FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_salas_updated_at ON salas;
CREATE TRIGGER update_salas_updated_at BEFORE UPDATE ON salas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_usuarios_aba_updated_at ON usuarios_aba;
CREATE TRIGGER update_usuarios_aba_updated_at BEFORE UPDATE ON usuarios_aba FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_especialidades_updated_at ON usuarios_especialidades;
CREATE TRIGGER update_usuarios_especialidades_updated_at BEFORE UPDATE ON usuarios_especialidades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_carteirinhas_updated_at ON carteirinhas;
CREATE TRIGGER update_carteirinhas_updated_at BEFORE UPDATE ON carteirinhas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_profissoes_updated_at ON usuarios_profissoes;
CREATE TRIGGER update_usuarios_profissoes_updated_at BEFORE UPDATE ON usuarios_profissoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_agendamentos_updated_at ON agendamentos;
CREATE TRIGGER update_agendamentos_updated_at BEFORE UPDATE ON agendamentos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_guias_updated_at ON guias;
CREATE TRIGGER update_guias_updated_at BEFORE UPDATE ON guias FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_fichas_updated_at ON fichas;
CREATE TRIGGER update_fichas_updated_at BEFORE UPDATE ON fichas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_fichas_pendentes_updated_at ON fichas_pendentes;
CREATE TRIGGER update_fichas_pendentes_updated_at BEFORE UPDATE ON fichas_pendentes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sessoes_updated_at ON sessoes;
CREATE TRIGGER update_sessoes_updated_at BEFORE UPDATE ON sessoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_execucoes_updated_at ON execucoes;
CREATE TRIGGER update_execucoes_updated_at BEFORE UPDATE ON execucoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_atendimentos_faturamento_updated_at ON atendimentos_faturamento;
CREATE TRIGGER update_atendimentos_faturamento_updated_at BEFORE UPDATE ON atendimentos_faturamento FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_divergencias_updated_at ON divergencias;
CREATE TRIGGER update_divergencias_updated_at BEFORE UPDATE ON divergencias FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_auditoria_execucoes_updated_at ON auditoria_execucoes;
CREATE TRIGGER update_auditoria_execucoes_updated_at BEFORE UPDATE ON auditoria_execucoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers para tabelas de Unimed Scraping
DROP TRIGGER IF EXISTS set_processing_status_timestamp ON processing_status;
CREATE TRIGGER set_processing_status_timestamp BEFORE UPDATE ON processing_status FOR EACH ROW EXECUTE FUNCTION update_processing_status_timestamp(); -- Usa a função específica

DROP TRIGGER IF EXISTS update_guias_queue_updated_at ON guias_queue;
CREATE TRIGGER update_guias_queue_updated_at BEFORE UPDATE ON guias_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); -- Usa a função geral

DROP TRIGGER IF EXISTS update_unimed_sessoes_updated_at ON unimed_sessoes_capturadas;
CREATE TRIGGER update_unimed_sessoes_updated_at BEFORE UPDATE ON unimed_sessoes_capturadas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); -- Usa a função geral

DROP TRIGGER IF EXISTS update_unimed_log_updated_at ON unimed_log_processamento;
CREATE TRIGGER update_unimed_log_updated_at BEFORE UPDATE ON unimed_log_processamento FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); -- Usa a função geral

-- Trigger para atualizar updated_at na nova tabela tipo_pagamento
DROP TRIGGER IF EXISTS set_tipo_pagamento_timestamp ON tipo_pagamento;
CREATE TRIGGER set_tipo_pagamento_timestamp
    BEFORE UPDATE ON tipo_pagamento
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Trigger para preencher atendimentos_faturamento (Exemplo de trigger de negócio)

-- Função simplificada para preencher atendimentos de faturamento (sem referências a tabelas faltantes)
CREATE OR REPLACE FUNCTION trigger_preencher_atendimento_faturamento()
RETURNS TRIGGER AS $$
BEGIN
    -- Alterando a condição para verificar quando o status do agendamento muda para 'realizado'
    IF NEW.schedule_status = 'realizado' AND (OLD.schedule_status IS NULL OR OLD.schedule_status <> 'realizado') THEN
        INSERT INTO atendimentos_faturamento (
            id_atendimento,
            agendamento_id_origem,
            carteirinha,
            paciente_id,
            paciente_nome,
            data_atendimento,
            hora_inicial,
            id_profissional,
            profissional_nome,
            procedimento_id,
            codigo_procedimento,
            nome_procedimento,
            status, -- Status inicial na tabela de faturamento
            codigo_faturamento
        )
        SELECT 
            NEW.id AS id_atendimento, -- FK para agendamentos (Supabase ID)
            NEW.id_origem AS agendamento_id_origem, -- ID original do ABA
            c.numero_carteirinha AS carteirinha,
            p.id AS paciente_id, -- FK para pacientes (Supabase ID)
            p.nome AS paciente_nome,
            DATE(NEW.schedule_date_start) AS data_atendimento,
            TO_CHAR(NEW.schedule_date_start, 'HH24:MI:SS')::TIME AS hora_inicial,
            u.id AS id_profissional, -- FK para usuarios (Supabase ID)
            u_aba.user_name || ' ' || u_aba.user_lastname AS profissional_nome, -- Nome do profissional do ABA
            proc.id AS procedimento_id, -- FK para procedimentos (Supabase ID)
            proc.codigo AS codigo_procedimento,
            proc.nome AS nome_procedimento,
            'confirmado' AS status, -- Status inicial
            NEW.schedule_codigo_faturamento AS codigo_faturamento
        FROM 
            pacientes p
        LEFT JOIN 
            carteirinhas c ON p.id = c.paciente_id
        LEFT JOIN
            usuarios_aba u_aba ON NEW.schedule_profissional_id = u_aba.id
        LEFT JOIN
            usuarios u ON u_aba.user_id = u.auth_user_id -- Assume que auth_user_id liga Supabase Auth a usuarios
        LEFT JOIN 
            procedimentos proc ON NEW.procedimento_id = proc.id
        WHERE 
            p.id_origem::varchar = NEW.schedule_pacient_id -- Comparação correta de tipos
        LIMIT 1; -- Garante que apenas um registro seja inserido por agendamento
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criação do trigger na tabela de agendamentos
DROP TRIGGER IF EXISTS trigger_agendamento_confirmado ON agendamentos;
CREATE TRIGGER trigger_agendamento_confirmado
    AFTER UPDATE ON agendamentos
    FOR EACH ROW
    EXECUTE FUNCTION trigger_preencher_atendimento_faturamento();

-- Trigger para enriquecer dados (atualmente não usado, prefira VIEW)
-- DROP TRIGGER IF EXISTS trigger_agendamento_enriquecer ON agendamentos;
-- CREATE TRIGGER trigger_agendamento_enriquecer
--     BEFORE INSERT OR UPDATE ON agendamentos
--     FOR EACH ROW
--     EXECUTE FUNCTION proc_agendamento_enriquecer_dados(); 
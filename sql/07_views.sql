--================ VIEWS =================

-- Vista para agendamentos completos com dados de relacionamentos
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
    carteirinhas c ON p.id = c.paciente_id -- Pode gerar duplicatas se paciente tiver >1 carteirinha. Ajustar se necessário.
LEFT JOIN 
    procedimentos proc ON a.procedimento_id = proc.id;
COMMENT ON VIEW vw_agendamentos_completos IS 'Visão que inclui dados completos de agendamentos com informações de pacientes e procedimentos';

-- Futura VIEW para agendamentos com status de vinculação (depende da função vincular_agendamentos)

-- VIEW para agendamentos com status de vinculação e nomes
CREATE OR REPLACE VIEW vw_agendamentos_com_status_vinculacao AS
SELECT 
    ag.*,
    p.nome AS paciente_nome,
    proc.nome AS procedimento_nome,
    tp.nome AS tipo_pagamento_nome,
    sa.room_name AS sala_nome,
    ua.user_name AS profissional_nome,
    es.nome AS especialidade_nome,
    ca.numero_carteirinha AS carteirinha_numero,
    ps.nome AS plano_saude_nome,
    lo.local_nome AS local_nome,
    CASE 
        WHEN s.id IS NOT NULL AND e.id IS NOT NULL THEN 'Completo'::text
        WHEN s.id IS NOT NULL THEN 'Ficha OK'::text
        WHEN e.id IS NOT NULL THEN 'Unimed OK'::text
        ELSE 'Pendente'::text
    END AS status_vinculacao,
    s.id IS NOT NULL AS possui_sessao_vinculada,
    e.id IS NOT NULL AS possui_execucao_vinculada
FROM 
    agendamentos ag
LEFT JOIN 
    pacientes p ON ag.paciente_id = p.id AND p.deleted_at IS NULL
LEFT JOIN
    procedimentos proc ON ag.procedimento_id = proc.id AND proc.deleted_at IS NULL
LEFT JOIN 
    tipo_pagamento tp ON proc.pagamento_id_origem = tp.id_origem AND tp.deleted_at IS NULL
LEFT JOIN 
    sessoes s ON ag.id = s.agendamento_id AND s.deleted_at IS NULL
LEFT JOIN 
    execucoes e ON ag.id = e.agendamento_id AND e.deleted_at IS NULL
LEFT JOIN
    salas sa ON ag.sala_id_supabase = sa.id AND sa.deleted_at IS NULL
LEFT JOIN 
    usuarios_aba ua ON ag.schedule_profissional_id = ua.id AND ua.deleted_at IS NULL
LEFT JOIN 
    especialidades es ON ag.especialidade_id_supabase = es.id AND es.deleted_at IS NULL
LEFT JOIN
    carteirinhas ca ON ag.paciente_id = ca.paciente_id AND ca.deleted_at IS NULL
LEFT JOIN 
    planos_saude ps ON ca.plano_saude_id = ps.id AND ps.deleted_at IS NULL
LEFT JOIN
    locais lo ON ag.local_id_supabase = lo.id AND lo.deleted_at IS NULL;

COMMENT ON VIEW vw_agendamentos_com_status_vinculacao IS 'Visão que junta agendamentos com status de vinculação, nomes de paciente, procedimento, tipo pagamento, sala, profissional, especialidade, carteirinha e plano de saúde.'; 
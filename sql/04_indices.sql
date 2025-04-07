--================ INDICES =================

-- Índices para tabelas base
CREATE INDEX IF NOT EXISTS idx_pacientes_nome ON pacientes(nome);
CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes(cpf);
CREATE INDEX IF NOT EXISTS idx_pacientes_deleted_at ON pacientes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_pacientes_importado ON pacientes(importado);
CREATE INDEX IF NOT EXISTS idx_pacientes_id_origem ON pacientes(id_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_registro_origem ON pacientes(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_atualizacao_origem ON pacientes(data_atualizacao_origem);

CREATE INDEX IF NOT EXISTS idx_planos_saude_nome ON planos_saude(nome);
CREATE INDEX IF NOT EXISTS idx_planos_saude_codigo ON planos_saude(codigo_operadora);
CREATE INDEX IF NOT EXISTS idx_planos_saude_deleted_at ON planos_saude(deleted_at);

CREATE INDEX IF NOT EXISTS idx_especialidades_nome ON especialidades(nome);
CREATE INDEX IF NOT EXISTS idx_especialidades_deleted_at ON especialidades(deleted_at);
CREATE INDEX IF NOT EXISTS idx_especialidades_id ON especialidades(especialidade_id);

CREATE INDEX IF NOT EXISTS idx_procedimentos_codigo ON procedimentos(codigo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_nome ON procedimentos(nome);
CREATE INDEX IF NOT EXISTS idx_procedimentos_tipo ON procedimentos(tipo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_deleted_at ON procedimentos(deleted_at);

CREATE INDEX IF NOT EXISTS idx_storage_nome ON storage(nome);
CREATE INDEX IF NOT EXISTS idx_storage_tipo ON storage(tipo_referencia);
CREATE INDEX IF NOT EXISTS idx_storage_deleted_at ON storage(deleted_at);

-- Índices para tipo_pagamento (nova tabela)
CREATE INDEX IF NOT EXISTS idx_tipo_pagamento_id_origem ON tipo_pagamento(id_origem);
CREATE INDEX IF NOT EXISTS idx_tipo_pagamento_nome ON tipo_pagamento(nome);
CREATE INDEX IF NOT EXISTS idx_tipo_pagamento_deleted_at ON tipo_pagamento(deleted_at);

-- Índices para tabelas de controle de importação
CREATE INDEX IF NOT EXISTS idx_controle_importacao_datas ON controle_importacao_pacientes(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_timestamp ON controle_importacao_pacientes(timestamp_importacao);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_datas ON controle_importacao_agendamentos(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_timestamp ON controle_importacao_agendamentos(timestamp_importacao);

-- Índices para tabelas do Sistema ABA
CREATE INDEX IF NOT EXISTS idx_profissoes_id ON profissoes(profissao_id);
CREATE INDEX IF NOT EXISTS idx_locais_id ON locais(local_id);
CREATE INDEX IF NOT EXISTS idx_salas_room_local_id ON salas(room_local_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_aba_id ON usuarios_aba(user_id);

-- Índices para tabelas de relacionamento
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_usuario ON usuarios_especialidades(usuario_aba_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_especialidade ON usuarios_especialidades(especialidade_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_deleted_at ON usuarios_especialidades(deleted_at);

CREATE INDEX IF NOT EXISTS idx_carteirinhas_paciente ON carteirinhas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_plano ON carteirinhas(plano_saude_id);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_numero ON carteirinhas(numero_carteirinha);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_deleted_at ON carteirinhas(deleted_at);

CREATE INDEX IF NOT EXISTS idx_usuarios_profissoes_usuario ON usuarios_profissoes(usuario_aba_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_profissoes_profissao ON usuarios_profissoes(profissao_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_profissoes_deleted_at ON usuarios_profissoes(deleted_at);

-- Índices para tabelas principais do fluxo
CREATE INDEX IF NOT EXISTS idx_agendamentos_paciente_id ON agendamentos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_procedimento_id ON agendamentos(procedimento_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_agendamento);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status);
CREATE INDEX IF NOT EXISTS idx_agendamentos_importado ON agendamentos(importado);
CREATE INDEX IF NOT EXISTS idx_agendamentos_id_origem ON agendamentos(id_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_registro_origem ON agendamentos(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_atualizacao_origem ON agendamentos(data_atualizacao_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_inicio ON agendamentos(schedule_date_start);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_fim ON agendamentos(schedule_date_end);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status_aba ON agendamentos(schedule_status);
CREATE INDEX IF NOT EXISTS idx_agendamentos_especialidade_aba ON agendamentos(schedule_especialidade_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_deleted_at ON agendamentos(deleted_at);
CREATE INDEX IF NOT EXISTS idx_agendamentos_room_id ON agendamentos(schedule_room_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_local_id ON agendamentos(schedule_local_id);

CREATE INDEX IF NOT EXISTS idx_guias_carteirinha ON guias(carteirinha_id);
CREATE INDEX IF NOT EXISTS idx_guias_procedimento ON guias(procedimento_id);
CREATE INDEX IF NOT EXISTS idx_guias_numero ON guias(numero_guia);
CREATE INDEX IF NOT EXISTS idx_guias_status ON guias(status);
CREATE INDEX IF NOT EXISTS idx_guias_deleted_at ON guias(deleted_at);

CREATE INDEX IF NOT EXISTS idx_fichas_guia ON fichas(guia_id);
CREATE INDEX IF NOT EXISTS idx_fichas_codigo ON fichas(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_fichas_numero_guia ON fichas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_fichas_data ON fichas(data_atendimento);
CREATE INDEX IF NOT EXISTS idx_fichas_status ON fichas(status);
CREATE INDEX IF NOT EXISTS idx_fichas_deleted_at ON fichas(deleted_at);
CREATE INDEX IF NOT EXISTS idx_fichas_paciente_id ON fichas(paciente_id); -- Índice Adicionado - Fase 4.4 Plano
CREATE UNIQUE INDEX IF NOT EXISTS idx_fichas_codigo_ficha_unique ON fichas (codigo_ficha) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_sessoes_ficha ON sessoes(ficha_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_guia ON sessoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_data ON sessoes(data_sessao);
CREATE INDEX IF NOT EXISTS idx_sessoes_status ON sessoes(status);
CREATE INDEX IF NOT EXISTS idx_sessoes_deleted_at ON sessoes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_sessoes_agendamento_id ON sessoes(agendamento_id); -- Índice Adicionado - Fase 4.4 Plano
CREATE INDEX IF NOT EXISTS idx_sessoes_ordem_execucao ON sessoes(ordem_execucao); -- Adicionado para otimizar buscas

CREATE INDEX IF NOT EXISTS idx_execucoes_guia ON execucoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_sessao ON execucoes(sessao_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_execucoes_numero_guia ON execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_execucoes_codigo_ficha ON execucoes(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_execucoes_carteirinha ON execucoes(paciente_carteirinha);
CREATE INDEX IF NOT EXISTS idx_execucoes_profissional ON execucoes(profissional_executante);
CREATE INDEX IF NOT EXISTS idx_execucoes_status_biometria ON execucoes(status_biometria);
CREATE INDEX IF NOT EXISTS idx_execucoes_deleted_at ON execucoes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_execucoes_agendamento_id ON execucoes(agendamento_id); -- Índice Adicionado - Fase 4.4 Plano
CREATE INDEX IF NOT EXISTS idx_execucoes_paciente_id ON execucoes(paciente_id); -- Índice Adicionado - Fase 4.6 Plano
CREATE INDEX IF NOT EXISTS idx_execucoes_ordem_execucao ON execucoes(ordem_execucao); -- Adicionado para otimizar buscas
CREATE INDEX IF NOT EXISTS idx_execucoes_link_manual ON execucoes(link_manual_necessario); -- Adicionado para otimizar buscas

CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_data ON atendimentos_faturamento(data_atendimento);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_profissional ON atendimentos_faturamento(id_profissional);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_id_atendimento ON atendimentos_faturamento(id_atendimento);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_agendamento_id_origem ON atendimentos_faturamento(agendamento_id_origem);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_execucao_id ON atendimentos_faturamento(execucao_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_sessao_id ON atendimentos_faturamento(sessao_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_ficha_id ON atendimentos_faturamento(ficha_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_paciente_id ON atendimentos_faturamento(paciente_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_status ON atendimentos_faturamento(status);

CREATE INDEX IF NOT EXISTS idx_divergencias_numero_guia ON divergencias(numero_guia);
CREATE INDEX IF NOT EXISTS idx_divergencias_tipo ON divergencias(tipo);
CREATE INDEX IF NOT EXISTS idx_divergencias_codigo_ficha ON divergencias(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_divergencias_status ON divergencias(status);
CREATE INDEX IF NOT EXISTS idx_divergencias_paciente ON divergencias(paciente_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_ficha ON divergencias(ficha_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_sessao ON divergencias(sessao_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_data_identificacao ON divergencias(data_identificacao);
CREATE INDEX IF NOT EXISTS idx_divergencias_deleted_at ON divergencias(deleted_at);

CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_data ON auditoria_execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_periodo ON auditoria_execucoes(data_inicial, data_final);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_status ON auditoria_execucoes(status);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_deleted_at ON auditoria_execucoes(deleted_at);

-- Índices para tabelas de Unimed Scraping
CREATE INDEX IF NOT EXISTS idx_processing_status_task_id ON processing_status(task_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_status ON processing_status(status);
CREATE INDEX IF NOT EXISTS idx_processing_status_dates ON processing_status(started_at, error_at, last_update);

CREATE INDEX IF NOT EXISTS idx_guias_queue_status ON guias_queue(status);
CREATE INDEX IF NOT EXISTS idx_guias_queue_task_id ON guias_queue(task_id);
CREATE INDEX IF NOT EXISTS idx_guias_queue_attempts ON guias_queue(attempts);

CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_numero_guia ON unimed_sessoes_capturadas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_status ON unimed_sessoes_capturadas(status);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_datas ON unimed_sessoes_capturadas(data_execucao, processed_at);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_task_id ON unimed_sessoes_capturadas(task_id);

CREATE INDEX IF NOT EXISTS idx_unimed_log_status ON unimed_log_processamento(status);
CREATE INDEX IF NOT EXISTS idx_unimed_log_sessao ON unimed_log_processamento(sessao_id);
CREATE INDEX IF NOT EXISTS idx_unimed_log_execucao ON unimed_log_processamento(execucao_id);

-- Adicionar índices para as novas colunas em procedimentos
CREATE INDEX IF NOT EXISTS idx_procedimentos_cod_fat_id_origem ON procedimentos(codigo_faturamento_id_origem);
CREATE INDEX IF NOT EXISTS idx_procedimentos_pag_id_origem ON procedimentos(pagamento_id_origem); 
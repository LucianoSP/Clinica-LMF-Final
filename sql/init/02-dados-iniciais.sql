-- Inserção de dados iniciais para o sistema da Clínica LMF
-- Este script adiciona dados para testes/desenvolvimento

-- Adicionando médicos de exemplo
INSERT INTO medicos (nome, crm, especialidade, email, telefone) VALUES
('Dr. Carlos Silva', 'CRM-12345', 'Clínico Geral', 'carlos.silva@clinicalmf.com', '(11) 98765-4321'),
('Dra. Maria Santos', 'CRM-54321', 'Cardiologia', 'maria.santos@clinicalmf.com', '(11) 91234-5678'),
('Dr. João Oliveira', 'CRM-67890', 'Ortopedia', 'joao.oliveira@clinicalmf.com', '(11) 99876-5432'),
('Dra. Ana Pereira', 'CRM-09876', 'Neurologia', 'ana.pereira@clinicalmf.com', '(11) 95678-1234');

-- Adicionando pacientes de exemplo
INSERT INTO pacientes (nome, data_nascimento, cpf, email, telefone, endereco) VALUES
('Roberto Almeida', '1985-06-15', '123.456.789-01', 'roberto@email.com', '(11) 97654-3210', 'Av. Paulista, 1000, São Paulo - SP'),
('Juliana Ferreira', '1990-04-22', '987.654.321-09', 'juliana@email.com', '(11) 96543-2109', 'Rua Augusta, 500, São Paulo - SP'),
('Marcos Oliveira', '1978-12-10', '456.789.123-45', 'marcos@email.com', '(11) 95432-1098', 'Rua Oscar Freire, 200, São Paulo - SP'),
('Camila Souza', '1995-08-30', '789.123.456-78', 'camila@email.com', '(11) 94321-0987', 'Alameda Santos, 800, São Paulo - SP'),
('Paulo Rodrigues', '1982-03-18', '321.654.987-32', 'paulo@email.com', '(11) 93210-9876', 'Av. Brigadeiro Faria Lima, 1500, São Paulo - SP');

-- Adicionando usuários de sistema (senha padrão: senha123)
INSERT INTO usuarios (nome, email, senha, perfil, medico_id) VALUES
('Admin Sistema', 'admin@clinicalmf.com', '$2b$10$X7o4c5Qk8K9xK5YmLjvQZ.oX3G6aJX1GcA1zN1JmVZ5GYqZZ1sH6G', 'admin', NULL),
('Carlos Silva', 'carlos.silva@clinicalmf.com', '$2b$10$X7o4c5Qk8K9xK5YmLjvQZ.oX3G6aJX1GcA1zN1JmVZ5GYqZZ1sH6G', 'medico', 1),
('Maria Santos', 'maria.santos@clinicalmf.com', '$2b$10$X7o4c5Qk8K9xK5YmLjvQZ.oX3G6aJX1GcA1zN1JmVZ5GYqZZ1sH6G', 'medico', 2),
('Recepção', 'recepcao@clinicalmf.com', '$2b$10$X7o4c5Qk8K9xK5YmLjvQZ.oX3G6aJX1GcA1zN1JmVZ5GYqZZ1sH6G', 'atendente', NULL);

-- Adicionando alguns agendamentos de exemplo
INSERT INTO agendamentos (paciente_id, medico_id, data_hora, status, observacoes) VALUES
(1, 1, DATE_ADD(NOW(), INTERVAL 1 DAY), 'agendado', 'Consulta de rotina'),
(2, 2, DATE_ADD(NOW(), INTERVAL 2 DAY), 'confirmado', 'Retorno de exames'),
(3, 3, DATE_ADD(NOW(), INTERVAL 3 DAY), 'agendado', 'Primeira consulta'),
(4, 4, DATE_ADD(NOW(), INTERVAL 1 WEEK), 'agendado', 'Avaliação de exames'),
(5, 1, DATE_ADD(NOW(), INTERVAL 2 WEEK), 'agendado', 'Consulta de rotina');

-- Adicionando algumas consultas já realizadas
INSERT INTO consultas (agendamento_id, diagnostico, prescricao, observacoes) VALUES
(1, 'Paciente saudável', 'Manter alimentação balanceada e exercícios físicos', 'Retorno em 6 meses'),
(2, 'Hipertensão leve', 'Losartana 50mg - 1 comprimido por dia', 'Monitorar pressão arterial e retornar em 1 mês');

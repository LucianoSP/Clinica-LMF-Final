-- Migração para corrigir a chave estrangeira na tabela controle_importacao_agendamentos
-- Data: 27/06/2024

-- 1. Primeiro removemos a restrição existente
ALTER TABLE controle_importacao_agendamentos 
DROP CONSTRAINT IF EXISTS controle_importacao_agendamentos_usuario_id_fkey;

-- 2. Adicionamos a nova restrição apontando para a tabela correta
ALTER TABLE controle_importacao_agendamentos
ADD CONSTRAINT controle_importacao_agendamentos_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

-- 3. Log da alteração
DO $$
BEGIN
    RAISE NOTICE 'Alterada a chave estrangeira da tabela controle_importacao_agendamentos para referenciar usuarios(id)';
END $$; 
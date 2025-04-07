-- Adicionar coluna codigo_aba na tabela pacientes
ALTER TABLE pacientes 
ADD COLUMN IF NOT EXISTS codigo_aba character varying(20) UNIQUE NOT NULL;

-- Criar índices para melhorar performance de busca por codigo_aba
CREATE INDEX IF NOT EXISTS idx_pacientes_codigo_aba ON pacientes(codigo_aba);

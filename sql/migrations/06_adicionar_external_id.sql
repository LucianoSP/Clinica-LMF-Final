-- Adicionar coluna external_id nas tabelas principais
ALTER TABLE pacientes 
ADD COLUMN IF NOT EXISTS external_id bigint,
ADD CONSTRAINT uq_pacientes_external_id UNIQUE (external_id);

ALTER TABLE carteirinhas
ADD COLUMN IF NOT EXISTS external_id bigint,
ADD CONSTRAINT uq_carteirinhas_external_id UNIQUE (external_id);

ALTER TABLE guias
ADD COLUMN IF NOT EXISTS external_id bigint,
ADD CONSTRAINT uq_guias_external_id UNIQUE (external_id);

-- Criar índices para melhorar performance de busca por external_id
CREATE INDEX IF NOT EXISTS idx_pacientes_external_id ON pacientes(external_id);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_external_id ON carteirinhas(external_id);
CREATE INDEX IF NOT EXISTS idx_guias_external_id ON guias(external_id);
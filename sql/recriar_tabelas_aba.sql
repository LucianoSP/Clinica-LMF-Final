

-- Remover tabelas relacionadas ao sistema ABA e suas dependências
-- Ordem: Tabelas de junção primeiro, depois as tabelas referenciadas.
DROP TABLE IF EXISTS usuarios_especialidades CASCADE;
DROP TABLE IF EXISTS usuarios_profissoes CASCADE;
DROP TABLE IF EXISTS agendamentos_profissionais CASCADE;
DROP TABLE IF EXISTS especialidades CASCADE;
DROP TABLE IF EXISTS usuarios_aba CASCADE;
DROP TABLE IF EXISTS profissoes CASCADE;
DROP TABLE IF EXISTS salas CASCADE;
DROP TABLE IF EXISTS locais CASCADE;

-- Recriar Função para atualizar updated_at automaticamente (caso não exista)
-- Geralmente já existe no Supabase, mas não custa garantir.
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Recriar tabela especialidades
CREATE TABLE IF NOT EXISTS especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    anexo text,
    status status_registro DEFAULT 'ativo'::status_registro, -- Garanta que o tipo ENUM status_registro existe
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    especialidade_id VARCHAR(255) UNIQUE -- Coluna para ID original do MySQL
);
-- Trigger e Índices para especialidades
DROP TRIGGER IF EXISTS update_especialidades_updated_at ON especialidades;
CREATE TRIGGER update_especialidades_updated_at BEFORE UPDATE ON especialidades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_especialidades_nome ON especialidades(nome);
CREATE INDEX IF NOT EXISTS idx_especialidades_deleted_at ON especialidades(deleted_at);
CREATE INDEX IF NOT EXISTS idx_especialidades_id ON especialidades(especialidade_id); -- Índice para ID original

-- Recriar tabela usuarios_aba
CREATE TABLE IF NOT EXISTS usuarios_aba (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE, -- Coluna para ID original do MySQL
    user_name VARCHAR(255) NOT NULL,
    user_lastname VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);
-- Trigger e Índice para usuarios_aba
DROP TRIGGER IF EXISTS update_usuarios_aba_updated_at ON usuarios_aba;
CREATE TRIGGER update_usuarios_aba_updated_at BEFORE UPDATE ON usuarios_aba FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_usuarios_aba_id ON usuarios_aba(user_id); -- Índice para ID original

-- Recriar tabela usuarios_especialidades (com referência corrigida)
CREATE TABLE IF NOT EXISTS usuarios_especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id uuid NOT NULL REFERENCES usuarios_aba(id) ON DELETE CASCADE, -- Referencia usuarios_aba
    especialidade_id uuid NOT NULL REFERENCES especialidades(id) ON DELETE CASCADE, -- Referencia especialidades
    principal boolean DEFAULT false,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE (usuario_aba_id, especialidade_id)
);
-- Trigger e Índices para usuarios_especialidades
DROP TRIGGER IF EXISTS update_usuarios_especialidades_updated_at ON usuarios_especialidades;
CREATE TRIGGER update_usuarios_especialidades_updated_at BEFORE UPDATE ON usuarios_especialidades FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_usuario ON usuarios_especialidades(usuario_aba_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_especialidade ON usuarios_especialidades(especialidade_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_deleted_at ON usuarios_especialidades(deleted_at);

-- Recriar tabela profissoes
CREATE TABLE IF NOT EXISTS profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profissao_id VARCHAR(255) UNIQUE, -- Coluna para ID original do MySQL
    profissao_name VARCHAR(255) NOT NULL,
    profissao_status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);
-- Trigger e Índice para profissoes
DROP TRIGGER IF EXISTS update_profissoes_updated_at ON profissoes;
CREATE TRIGGER update_profissoes_updated_at BEFORE UPDATE ON profissoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_profissoes_id ON profissoes(profissao_id); -- Índice para ID original

-- Recriar tabela usuarios_profissoes (com referência corrigida)
CREATE TABLE IF NOT EXISTS usuarios_profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id UUID NOT NULL REFERENCES usuarios_aba(id) ON DELETE CASCADE, -- Referencia usuarios_aba
    profissao_id UUID NOT NULL REFERENCES profissoes(id) ON DELETE CASCADE, -- Referencia profissoes
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ,
    UNIQUE(usuario_aba_id, profissao_id)
);
-- Trigger e Índices para usuarios_profissoes
DROP TRIGGER IF EXISTS update_usuarios_profissoes_updated_at ON usuarios_profissoes;
CREATE TRIGGER update_usuarios_profissoes_updated_at BEFORE UPDATE ON usuarios_profissoes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_usuarios_profissoes_usuario_aba_id ON usuarios_profissoes(usuario_aba_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_profissoes_profissao_id ON usuarios_profissoes(profissao_id);

-- Recriar tabela locais
CREATE TABLE IF NOT EXISTS locais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    local_id VARCHAR(255) UNIQUE, -- Coluna para ID original do MySQL
    local_nome VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);
-- Trigger e Índice para locais
DROP TRIGGER IF EXISTS update_locais_updated_at ON locais;
CREATE TRIGGER update_locais_updated_at BEFORE UPDATE ON locais FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_locais_id ON locais(local_id); -- Índice para ID original

-- Recriar tabela salas
CREATE TABLE IF NOT EXISTS salas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id VARCHAR(255) UNIQUE, -- Coluna para ID original do MySQL (room_id)
    room_local_id VARCHAR(255), -- Coluna para ID original do local (room_local_id)
    room_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);
-- Trigger e Índices para salas
DROP TRIGGER IF EXISTS update_salas_updated_at ON salas;
CREATE TRIGGER update_salas_updated_at BEFORE UPDATE ON salas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE INDEX IF NOT EXISTS idx_salas_room_id ON salas(room_id); -- Índice para ID original
CREATE INDEX IF NOT EXISTS idx_salas_room_local_id ON salas(room_local_id);

-- Recriar tabela agendamentos_profissionais
CREATE TABLE IF NOT EXISTS agendamentos_profissionais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES agendamentos(id) ON DELETE CASCADE, -- Garanta que a tabela agendamentos existe e está estável
    professional_id UUID REFERENCES usuarios_aba(id) ON DELETE CASCADE, -- Referencia usuarios_aba
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ,
    UNIQUE(schedule_id, professional_id)
);
-- Trigger para agendamentos_profissionais
DROP TRIGGER IF EXISTS update_agendamentos_profissionais_updated_at ON agendamentos_profissionais;
CREATE TRIGGER update_agendamentos_profissionais_updated_at BEFORE UPDATE ON agendamentos_profissionais FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();



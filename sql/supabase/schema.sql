-- Esquema de banco de dados para Supabase
-- Execute estas queries no Editor SQL do Supabase

-- Configurar o esquema
CREATE SCHEMA IF NOT EXISTS "public";

-- Tabela de pacientes
CREATE TABLE IF NOT EXISTS "public"."pacientes" (
    "id" SERIAL PRIMARY KEY,
    "nome" TEXT NOT NULL,
    "cpf" TEXT UNIQUE,
    "data_nascimento" DATE,
    "telefone" TEXT,
    "email" TEXT,
    "endereco" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de médicos
CREATE TABLE IF NOT EXISTS "public"."medicos" (
    "id" SERIAL PRIMARY KEY,
    "nome" TEXT NOT NULL,
    "crm" TEXT UNIQUE,
    "especialidade" TEXT,
    "telefone" TEXT,
    "email" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS "public"."agendamentos" (
    "id" SERIAL PRIMARY KEY,
    "paciente_id" INTEGER REFERENCES "public"."pacientes"("id"),
    "medico_id" INTEGER REFERENCES "public"."medicos"("id"),
    "data_hora" TIMESTAMP WITH TIME ZONE NOT NULL,
    "status" TEXT DEFAULT 'agendado',
    "observacoes" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de consultas
CREATE TABLE IF NOT EXISTS "public"."consultas" (
    "id" SERIAL PRIMARY KEY,
    "agendamento_id" INTEGER REFERENCES "public"."agendamentos"("id"),
    "diagnostico" TEXT,
    "prescricao" TEXT,
    "observacoes" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configurar RLS (Row Level Security)
ALTER TABLE "public"."pacientes" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."medicos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."agendamentos" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."consultas" ENABLE ROW LEVEL SECURITY;

-- Criar políticas para permitir acesso autenticado
CREATE POLICY "Acesso completo para usuários autenticados" 
ON "public"."pacientes" FOR ALL TO authenticated 
USING (true);

CREATE POLICY "Acesso completo para usuários autenticados" 
ON "public"."medicos" FOR ALL TO authenticated 
USING (true);

CREATE POLICY "Acesso completo para usuários autenticados" 
ON "public"."agendamentos" FOR ALL TO authenticated 
USING (true);

CREATE POLICY "Acesso completo para usuários autenticados" 
ON "public"."consultas" FOR ALL TO authenticated 
USING (true);

-- Triggers para atualizar automaticamente o campo updated_at
CREATE OR REPLACE FUNCTION "public"."set_updated_at"()
RETURNS TRIGGER AS $$
BEGIN
  NEW."updated_at" = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER "set_pacientes_updated_at"
BEFORE UPDATE ON "public"."pacientes"
FOR EACH ROW
EXECUTE FUNCTION "public"."set_updated_at"();

CREATE TRIGGER "set_medicos_updated_at"
BEFORE UPDATE ON "public"."medicos"
FOR EACH ROW
EXECUTE FUNCTION "public"."set_updated_at"();

CREATE TRIGGER "set_agendamentos_updated_at"
BEFORE UPDATE ON "public"."agendamentos"
FOR EACH ROW
EXECUTE FUNCTION "public"."set_updated_at"();

CREATE TRIGGER "set_consultas_updated_at"
BEFORE UPDATE ON "public"."consultas"
FOR EACH ROW
EXECUTE FUNCTION "public"."set_updated_at"();

-- Índices para melhorar performance
CREATE INDEX IF NOT EXISTS "idx_pacientes_nome" ON "public"."pacientes" ("nome");
CREATE INDEX IF NOT EXISTS "idx_medicos_nome" ON "public"."medicos" ("nome");
CREATE INDEX IF NOT EXISTS "idx_medicos_especialidade" ON "public"."medicos" ("especialidade");
CREATE INDEX IF NOT EXISTS "idx_agendamentos_data_hora" ON "public"."agendamentos" ("data_hora");

-- Tabelas de mapeamento para importação de agendamentos do MySQL

-- Tabela de mapeamento para pacientes
CREATE TABLE IF NOT EXISTS mapeamento_ids_pacientes (
  id_mysql INT NOT NULL,
  id_supabase UUID NOT NULL,
  PRIMARY KEY (id_mysql)
);

-- Tabela de mapeamento para salas
CREATE TABLE IF NOT EXISTS mapeamento_ids_salas (
  id_mysql INT NOT NULL,
  id_supabase UUID NOT NULL,
  PRIMARY KEY (id_mysql)
);

-- Tabela de mapeamento para especialidades
CREATE TABLE IF NOT EXISTS mapeamento_ids_especialidades (
  id_mysql INT NOT NULL,
  id_supabase UUID NOT NULL,
  PRIMARY KEY (id_mysql)
);

-- Tabela de mapeamento para locais
CREATE TABLE IF NOT EXISTS mapeamento_ids_locais (
  id_mysql INT NOT NULL,
  id_supabase UUID NOT NULL,
  PRIMARY KEY (id_mysql)
);

-- Tabela de mapeamento para formas de pagamento
CREATE TABLE IF NOT EXISTS mapeamento_ids_pagamentos (
  id_mysql INT NOT NULL,
  id_supabase UUID NOT NULL,
  PRIMARY KEY (id_mysql)
);

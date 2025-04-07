--================ EXTENSÕES =================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


--================ TIPOS ENUM =================

-- Tipos enumerados
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_usuario') THEN
        CREATE TYPE tipo_usuario AS ENUM (
            'admin',
            'profissional',
            'operador',
            'sistema'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_registro') THEN
        CREATE TYPE status_registro AS ENUM (
            'ativo',
            'inativo',
            'pendente'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_carteirinha') THEN
        CREATE TYPE status_carteirinha AS ENUM (
            'ativa',
            'inativa',
            'suspensa',
            'vencida'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_guia') THEN
        CREATE TYPE status_guia AS ENUM (
            'rascunho',
            'pendente',
            'autorizada',
            'negada',
            'cancelada',
            'executada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_procedimento') THEN
        CREATE TYPE tipo_procedimento AS ENUM (
            'consulta',
            'exame',
            'procedimento',
            'internacao'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_ficha') THEN
        CREATE TYPE status_ficha AS ENUM (
            'pendente',
            'conferida',
            'faturada',
            'cancelada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_biometria') THEN
        CREATE TYPE status_biometria AS ENUM (
            'nao_verificado',
            'verificado',
            'falha'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_sessao') THEN
        CREATE TYPE status_sessao AS ENUM (
            'pendente',
            'executada',
            'faturada',
            'cancelada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_divergencia') THEN
        CREATE TYPE tipo_divergencia AS ENUM (
            'ficha_sem_execucao',
            'execucao_sem_ficha',
            'sessao_sem_assinatura',
            'data_divergente',
            'guia_vencida',
            'quantidade_excedida',
            'falta_data_execucao',
            'duplicidade'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_divergencia') THEN
        CREATE TYPE status_divergencia AS ENUM ('pendente', 'em_analise', 'resolvida', 'cancelada');
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_guia') THEN
        CREATE TYPE tipo_guia AS ENUM (
            'consulta',
            'exame',
            'procedimento',
            'internacao'
        );
    END IF;
END$$;

-- Adicionar tipo enum para status de agendamento
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_agendamento') THEN
        CREATE TYPE status_agendamento AS ENUM (
            'agendado',
            'cancelado',
            'realizado',
            'faltou'
        );
    END IF;
END$$;

-- enum para tipo de unidade
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_unidade') THEN
        CREATE TYPE tipo_unidade AS ENUM (
            'Unidade Oeste',
            'República do Líbano'
        );
    END IF;
END$$; 
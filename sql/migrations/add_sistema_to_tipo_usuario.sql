-- Migração para adicionar o valor 'sistema' ao enum tipo_usuario
-- Data: 12/03/2025

-- Adiciona o valor 'sistema' ao enum tipo_usuario
ALTER TYPE tipo_usuario ADD VALUE 'sistema';

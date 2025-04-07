#!/bin/bash

# Script para aplicar a migração de agendamentos no banco de dados Supabase
# Autor: Claude AI
# Data: 2024

echo "Iniciando aplicação da migração para corrigir a estrutura de agendamentos..."

# Aplicar a migração SQL
psql -h wpufnegczzdbuztgpxab.supabase.co -U postgres -d postgres -f sql/migrations/20_remover_campos_redundantes_agendamentos.sql

if [ $? -eq 0 ]; then
    echo "Migração aplicada com sucesso!"
    echo "A estrutura de agendamentos foi atualizada para usar o modelo relacional corretamente."
    echo "Agora a importação de agendamentos deve funcionar sem erros de 'carteirinha column not found'."
else
    echo "Erro ao aplicar a migração. Verifique as credenciais e a conexão com o banco de dados."
fi

# Informações adicionais
echo ""
echo "INSTRUÇÕES ADICIONAIS:"
echo "======================"
echo "1. A migração criou uma view 'vw_agendamentos_completos' que já inclui todos os"
echo "   dados complementares de pacientes e procedimentos."
echo "2. Para importar agendamentos, continue usando a API como antes, mas"
echo "   o código agora está adaptado para remover campos redundantes."
echo "3. Se precisar de acesso direto aos dados completos, use a view criada ao invés da tabela."
echo ""
echo "Exemplo de uso da view:"
echo "SELECT * FROM vw_agendamentos_completos WHERE data_agendamento > '2024-01-01';" 
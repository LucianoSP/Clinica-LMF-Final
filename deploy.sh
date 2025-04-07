#!/bin/bash

# Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Arquivo .env não encontrado. Criando a partir do .env-example..."
    cp .env-example .env
    echo "Por favor, edite o arquivo .env com suas configurações antes de continuar."
    exit 1
fi

# Inicia os contêineres Docker
echo "Iniciando os contêineres Docker..."
docker-compose up -d

echo "Aguardando os serviços iniciarem..."
sleep 5

echo "Aplicação iniciada com sucesso!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"

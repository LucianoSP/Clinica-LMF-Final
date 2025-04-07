# Instruções para Deploy com Docker

Este documento contém instruções detalhadas para implantar a aplicação Clínica LMF - Final usando Docker.

## Pré-requisitos

- Docker Desktop instalado
- Git instalado
- Acesso ao Supabase

## Arquivos de Configuração

- `docker-compose.yml`: Orquestra os serviços de frontend e backend
- `Dockerfile.backend`: Configura a imagem para o backend (Python)
- `frontend/Dockerfile`: Configura a imagem para o frontend (Next.js)

## Variáveis de Ambiente

Configure o arquivo `.env` com base no `.env-example` fornecido, incluindo:

- Credenciais do Supabase
- Configurações do MySQL remoto (para importação)
- Configurações de portas e ambiente

## Instruções para Deploy

1. Clone o repositório
2. Configure o arquivo `.env`
3. Execute o script de deploy (`deploy.bat` ou `deploy.sh`)
4. Acesse a aplicação em http://localhost:3000

## Suporte

Em caso de problemas, verifique os logs do Docker e as configurações de ambiente.

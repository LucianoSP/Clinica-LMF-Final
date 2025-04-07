# Clínica LMF - Final

Repositório para o projeto da Clínica LMF - Versão Final.

## Sobre o Projeto

Este repositório contém o código fonte do sistema da Clínica LMF, que inclui funcionalidades para gerenciamento de pacientes, agendamentos, consultas e outros aspectos relacionados ao funcionamento da clínica.

## Estrutura do Projeto

- `frontend/`: Aplicação Next.js para interface do usuário
- `backend/`: Módulos da API Python
- `main.py`: Script principal para iniciar o backend
- `docs/`: Documentação do projeto

## Requisitos

- Docker e Docker Compose
- Git
- Conta no Supabase (para banco de dados e autenticação)

## Como Utilizar

### Instalação com Docker (Recomendado)

1. Clone o repositório:
   ```bash
   git clone https://github.com/LucianoSP/Clinica-LMF-Final.git
   cd Clinica-LMF-Final
   ```

2. Configure as variáveis de ambiente:
   ```bash
   cp .env-example .env
   ```
   Edite o arquivo `.env` com suas configurações, incluindo as credenciais do Supabase e do MySQL remoto para importação.

3. Inicie os contêineres Docker:
   - **Windows**: Execute o arquivo `deploy.bat`
   - **Linux/Mac**: Execute o script `sh deploy.sh`

4. Acesse a aplicação:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Configuração do Supabase

Este projeto utiliza o Supabase para banco de dados e autenticação. Você precisará:

1. Criar um projeto no [Supabase](https://supabase.com/)
2. Obter as credenciais de API (URL e chaves) e configurá-las no arquivo `.env`

### Importação de Dados

O sistema está configurado para acessar um banco de dados MySQL remoto para importação de dados para o Supabase. Configure as credenciais do MySQL remoto no arquivo `.env`.

### Instalação Manual

#### Frontend (Next.js)

1. Navegue até a pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Configure o arquivo `.env.local` com as variáveis do Supabase
   ```
   NEXT_PUBLIC_SUPABASE_URL=sua-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=sua-chave
   ```

4. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

#### Backend (Python)

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente para o Supabase e MySQL remoto

4. Inicie o servidor:
   ```bash
   python main.py
   ```

## Suporte

Para dúvidas ou suporte, entre em contato com a equipe do projeto.

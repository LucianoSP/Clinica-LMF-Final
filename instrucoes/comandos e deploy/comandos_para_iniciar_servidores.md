# Comandos para Iniciar Servidores

Este documento contém instruções detalhadas sobre como iniciar os servidores do projeto ClinicalMF.

## Estrutura do Projeto

O projeto está organizado em duas partes principais:
- **Frontend**: Aplicação Next.js
- **Backend**: API FastAPI
- **Arquivo principal para iniciar o projeto**: main.py na pasta raiz

Cada parte tem seu próprio conjunto de comandos para inicialização.

## Iniciando o Frontend

### Opção 1: Usando Scripts NPM na Pasta Raiz

A partir da pasta raiz do projeto (`D:\CODIGO\clinicalmf-producao`), você pode usar os seguintes comandos:

```powershell
# Iniciar o servidor de desenvolvimento
npm run frontend:dev

# Construir o projeto para produção
npm run frontend:build

# Iniciar o servidor em modo de produção
npm run frontend:start
```

### Opção 2: Usando o Arquivo Batch

Na pasta raiz do projeto, você pode executar o arquivo batch:

```powershell
# No Windows
.\start-frontend.bat
```

### Opção 3: Navegando para a Pasta Frontend (Recomendado)

Você também pode navegar manualmente para a pasta frontend e executar os comandos diretamente:

```powershell
# Navegar para a pasta frontend
cd frontend

# Iniciar o servidor de desenvolvimento
npm run dev

# Construir o projeto para produção
npm run build

# Iniciar o servidor em modo de produção
npm run start
```

## Iniciando o Backend

### Opção 1: Usando Scripts NPM na Pasta Raiz

A partir da pasta raiz do projeto, você pode usar o seguinte comando:

```powershell
# Iniciar o servidor backend
npm run backend:start
```

### Opção 2: Executando o Arquivo Principal (Recomendado)

O backend deve ser iniciado a partir do arquivo main.py na pasta raiz do projeto, não a partir do app.py na pasta backend:

```powershell
# Executar na pasta raiz do projeto
python main.py
```

## Solução de Problemas

### Erro: "Missing script: dev"

Se você encontrar o erro:

```
npm error Missing script: "dev"
```

Isso significa que você está tentando executar o comando `npm run dev` na pasta raiz do projeto, onde esse script não está definido. Use uma das opções acima para iniciar o servidor corretamente.

### Erro: Separador de Comandos no PowerShell

No Windows com PowerShell, o separador de comandos `&&` não funciona. Use ponto e vírgula (`;`) para executar múltiplos comandos:

```powershell
# Forma INCORRETA no PowerShell
cd frontend && npm run dev

# Forma CORRETA no PowerShell
cd frontend; npm run dev
```

### Processos Node.js Travados

Se o servidor não iniciar corretamente ou você encontrar erros de porta já em uso, pode ser necessário encerrar processos Node.js existentes:

```powershell
# No Windows
taskkill /F /IM node.exe /T
```

### Limpeza de Cache

Se você encontrar problemas de carregamento ou erros no console, pode ser útil limpar o cache do Next.js:

```powershell
# Navegar para a pasta frontend
cd frontend

# Remover a pasta .next
rmdir /S /Q .next

# Reinstalar dependências
npm install

# Reconstruir o projeto
npm run build
```

## Acessando as Aplicações

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

## Ferramentas de Diagnóstico

O frontend inclui uma ferramenta de diagnóstico que pode ser ativada pressionando `Ctrl+Shift+D` enquanto a aplicação está carregada. Ela mostra informações sobre o status da conexão e possíveis erros.

## Notas Adicionais

- O servidor frontend em modo de desenvolvimento (`npm run dev`) oferece recarga automática quando os arquivos são alterados.
- O servidor frontend em modo de produção (`npm run start`) é mais rápido, mas não oferece recarga automática.
- O backend deve estar em execução para que o frontend possa se comunicar com o banco de dados e realizar operações.

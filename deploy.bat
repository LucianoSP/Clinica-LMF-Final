@echo off
echo Verificando se o arquivo .env existe...

if not exist .env (
    echo Arquivo .env nao encontrado. Criando a partir do .env-example...
    copy .env-example .env
    echo Por favor, edite o arquivo .env com suas configuracoes antes de continuar.
    pause
    exit /b 1
)

echo Iniciando os conteineres Docker...
docker-compose up -d

echo Aguardando os servicos iniciarem...
timeout /t 5 /nobreak > nul

echo Aplicacao iniciada com sucesso!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
pause

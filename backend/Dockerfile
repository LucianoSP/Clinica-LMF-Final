FROM python:3.10-slim

WORKDIR /app

# Instalar dependências necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos
COPY . .

# Expor a porta do backend
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["python", "main.py"]

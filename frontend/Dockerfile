FROM node:18-alpine

WORKDIR /app

# Copiar package.json e package-lock.json para instalar dependências
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar o resto dos arquivos do projeto
COPY . .

# Gerar o build
RUN npm run build

# Expor a porta 3000
EXPOSE 3000

# Iniciar o servidor
CMD ["npm", "start"]

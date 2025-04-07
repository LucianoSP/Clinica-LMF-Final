# Instruções Gerais

## Matar sessões do Node em execução
```bash
taskkill /f /im node.exe
```

## Criar ambiente virtual VENV Python
```bash
# Verificar versão do Python
python --version

# Navegar até a pasta do projeto
cd /caminho/para/a/pasta/do/seu/projeto

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Desativar ambiente virtual quando terminar
deactivate
```

## Inicializar Git
```bash
# Navegar até a pasta do projeto
cd /caminho/para/a/pasta/do/seu/projeto

# Inicializar repositório Git
git init

# Criar README inicial
echo "# clinicalmf-producao" >> README.md

# Adicionar README ao stage
git add README.md

# Fazer o primeiro commit
git commit -m "first commit"

# Adicionar repositório remoto
git remote add origin https://github.com/LucianoSP/clinicalmf-producao.git

# Renomear branch principal para main
git branch -M main

# Enviar para o repositório remoto
git push -u origin main
```

## Melhores Práticas para Trabalhar em Equipe

Para trabalhar em um projeto Next.js e Python em um repositório GitHub com outra pessoa, você precisa seguir algumas boas práticas de colaboração:

### Configuração inicial

1. **Clone o repositório**
   ```bash
   git clone https://github.com/usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. **Configure seu ambiente de desenvolvimento**
   - Para o Next.js (frontend):
   ```bash
   cd frontend  # ou pasta onde está o código Next.js
   npm install  # ou yarn install
   ```
   
   - Para o Python (backend):
   ```bash
   cd backend  # ou pasta onde está o código Python
   python -m venv venv  # cria ambiente virtual
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Fluxo de trabalho colaborativo

1. **Sincronize antes de começar a trabalhar**
   ```bash
   git pull origin main  # ou a branch principal
   ```

2. **Crie uma branch para sua tarefa**
   ```bash
   git checkout -b feature/nome-da-sua-funcionalidade
   ```

3. **Faça commits frequentes com mensagens claras**
   ```bash
   git add .
   git commit -m "Adiciona funcionalidade de login"
   ```

4. **Envie sua branch para o repositório remoto**
   ```bash
   git push origin feature/nome-da-sua-funcionalidade
   ```

5. **Crie um Pull Request no GitHub** para revisão do código

### Melhores práticas

- **Comunique-se regularmente** com seu parceiro sobre quais arquivos estão sendo modificados
- **Use issues no GitHub** para rastrear tarefas
- **Faça revisões de código** através de Pull Requests
- **Defina padrões de código** para manter consistência
- **Configure ferramentas de linting** (ESLint para Next.js, Flake8/Black para Python)
- **Documente seu código e APIs**

### Lidando com conflitos

Se ocorrerem conflitos ao tentar mesclar seu código:

```bash
git pull origin main
# Resolver conflitos nos arquivos indicados
git add .
git commit -m "Resolve conflitos de merge"
git push origin feature/nome-da-sua-funcionalidade
```

## Pull Request

O Pull Request (PR) é uma funcionalidade essencial do Git para colaboração em equipe, não uma função específica do Cursor IDE. Vou explicar o que é e como você pode criar um:

### O que é um Pull Request?

Um Pull Request é um mecanismo que permite que você notifique outros membros da equipe que você completou uma funcionalidade em uma branch separada. É basicamente um pedido para que suas alterações sejam "puxadas" (pulled) e mescladas na branch principal (geralmente main ou master).

### Para que serve?

- **Revisão de código**: Permite que outros desenvolvedores revisem suas alterações antes da mesclagem
- **Discussão**: Oferece um espaço para discutir alterações propostas
- **Testes automatizados**: Muitos repositórios executam testes automaticamente quando um PR é aberto
- **Documentação**: Registra mudanças e justificativas para referência futura
- **Controle de qualidade**: Ajuda a manter a qualidade do código na branch principal

### Como criar um Pull Request (mesmo usando o Cursor IDE):

O Cursor não tem funcionalidade nativa para criar PRs diretamente. Em vez disso, você:

1. **Trabalhe na sua branch local** dentro do Cursor
2. **Faça commit e push das mudanças** para o repositório remoto:
   ```bash
   git add .
   git commit -m "Descrição das alterações"
   git push origin nome-da-sua-branch
   ```
3. **Vá para o GitHub** no seu navegador web
4. Navegue até o repositório e você verá um banner sugerindo criar um PR a partir da sua branch recém-enviada
5. Clique em "Compare & pull request"
6. Preencha a descrição do PR, adicione revisores e clique em "Create pull request"

Para reverter seu ambiente local para um commit específico do Git, você pode usar o comando:
git reset --hard [hash_do_commit]
git checkout nome_da_sua_branch

Para descartar suas alterações locais e forçar o repositório remoto a ficar igual ao seu estado local atual (apagando commits posteriores ao que sincronizou):


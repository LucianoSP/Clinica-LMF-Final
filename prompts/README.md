# Repositório de Prompts para Extração de Dados

Este diretório contém prompts personalizados para extração de dados de documentos PDF usando modelos de IA (Claude, Gemini e Mistral).

## Estrutura do Repositório

```
prompts/
├── unimed/         # Prompts específicos para documentos da Unimed
│   ├── padrao.md   # Prompt padrão para fichas da Unimed
│   └── especial.md # Prompt para casos especiais da Unimed
├── outros/         # Prompts para outros convênios ou tipos de documentos
└── README.md       # Este arquivo
```

## Como Usar

Para usar um prompt personalizado, especifique o caminho relativo no campo "Arquivo de Prompt Personalizado" na interface de upload ou no parâmetro `prompt_path` da API:

```bash
# Exemplo de uso via API
curl -X POST http://seu-servidor/api/upload-pdf \
  -F "files=@documento.pdf" \
  -F "modelo_ia=claude" \
  -F "prompt_path=prompts/unimed/padrao.md"
```

## Convenções de Nomenclatura

- Use nomes descritivos e consistentes (ex: `convenio_tipo_versao.md`)
- Inclua o nome do convênio ou tipo de documento como prefixo
- Para versões atualizadas, use sufixos numéricos (ex: `unimed_padrao_v2.md`)

## Estrutura Recomendada para Prompts

Cada arquivo de prompt deve seguir esta estrutura:

```markdown
# Título do Prompt
# Versão: X.Y
# Data: DD/MM/AAAA
# Autor: Nome do Autor

Descrição do propósito do prompt...

{
    "formato_json": "esperado"
}

Regras de extração:
1. Regra 1
2. Regra 2
...

Histórico de alterações:
- DD/MM/AAAA: Descrição da alteração
```

## Documentação Completa

Para mais detalhes sobre criação e uso de prompts personalizados, consulte a documentação específica em `instrucoes/prompts_personalizados.md`. 
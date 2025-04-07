# Documentação - Sistema de Download de Guias Unimed

Este documento descreve o funcionamento dos scripts para listagem e download de guias em PDF da Unimed Goiânia.

## Visão Geral

O sistema é composto por três scripts principais:

1. `listar_guias_disponiveis.py` - Lista as guias disponíveis para uma data específica
2. `baixar_guia_pdf.py` - Baixa o PDF de uma guia específica (por número e data)
3. `baixar_multiplas_guias.py` - Baixa múltiplas guias dentro de um intervalo de datas

Todos os scripts utilizam a biblioteca Playwright para automação de navegador, garantindo maior confiabilidade no processo de scraping e download.

## Requisitos

- Python 3.8 ou superior
- Playwright (`pip install playwright`)
- Execução do comando `playwright install` após a instalação
- Variáveis de ambiente configuradas:
  - `UNIMED_USERNAME`: Usuário para login na Unimed
  - `UNIMED_PASSWORD`: Senha para login na Unimed

## Script: listar_guias_disponiveis.py

### Funcionalidade
Lista todas as guias disponíveis na Unimed para uma data específica, navegando por todas as páginas de resultados.

### Parâmetros
- `--data_atendimento`: Data de atendimento no formato dd/mm/aaaa
- `--salvar`: (opcional) Salva os resultados em um arquivo CSV

### Saída
Retorna uma lista de dicionários contendo:
- `numero_guia`: Número da guia
- `data`: Data do atendimento
- `hora`: Hora do atendimento
- `informacao_adicional`: Informações extras sobre o atendimento

### Exemplo de uso
```bash
python listar_guias_disponiveis.py --data_atendimento "14/03/2024" --salvar
```

## Script: baixar_guia_pdf.py

### Funcionalidade
Baixa o PDF de uma guia específica, identificada por seu número e data de atendimento.

### Estratégias de Download
O script utiliza múltiplas estratégias para baixar o PDF:
1. Busca primeiramente pela guia usando filtros de data
2. Localiza o botão de impressão ou links relacionados
3. Tenta usar o link "Todas as guias" quando disponível
4. Em caso de falha nos métodos acima, gera um PDF a partir da página atual

### Parâmetros
- `--numero_guia`: Número da guia para download
- `--data_atendimento`: Data de atendimento no formato dd/mm/aaaa

### Saída
- Salva o PDF no diretório `guias_pdf` com o nome no formato `{numero_guia}_{data_atendimento}.pdf`
- Retorna o caminho do arquivo PDF salvo ou None em caso de falha

### Exemplo de uso
```bash
python baixar_guia_pdf.py --numero_guia 45375285 --data_atendimento "14/03/2024"
```

## Script: baixar_multiplas_guias.py

### Funcionalidade
Automatiza o download de múltiplas guias em um intervalo de datas, com opção de limitar o número máximo de guias.

### Fluxo de trabalho
1. Lista todas as guias disponíveis para cada data no intervalo
2. Baixa o PDF de cada guia encontrada
3. Gera um resumo da operação ao final

### Parâmetros
- `--data_inicio`: Data inicial no formato dd/mm/aaaa
- `--data_fim`: Data final no formato dd/mm/aaaa
- `--max_guias`: (opcional) Número máximo de guias a baixar

### Exemplos de uso
```bash
# Baixar todas as guias de um dia específico
python baixar_multiplas_guias.py --data_inicio "14/03/2024" --data_fim "14/03/2024"

# Baixar guias em um intervalo de datas
python baixar_multiplas_guias.py --data_inicio "01/03/2024" --data_fim "31/03/2024"

# Limitar o número de guias baixadas
python baixar_multiplas_guias.py --data_inicio "01/03/2024" --data_fim "31/03/2024" --max_guias 20
```

## Armazenamento de arquivos

Os scripts criam e utilizam os seguintes diretórios:
- `guias_pdf`: Armazena os PDFs das guias baixadas
- `resultados`: Armazena arquivos CSV de listagens de guias

## Tratamento de Erros

Os scripts incluem tratamento robusto de erros:
- Verificação de elementos ausentes na página
- Estratégias alternativas para download de PDFs
- Retry automático em caso de falhas intermitentes
- Logs detalhados para facilitar a depuração

## Limitações conhecidas

- O sistema depende da estrutura do site da Unimed Goiânia, que pode mudar sem aviso prévio
- Algumas guias podem não ser baixadas devido a particularidades na forma como são apresentadas no sistema
- Ocasionalmente, o download pode falhar devido a timeouts ou questões de rede

## Melhorias futuras

- Implementação de captcha bypass (se necessário)
- Paralelização do download de múltiplas guias
- Interface gráfica para facilitar o uso
- Integração com armazenamento em nuvem

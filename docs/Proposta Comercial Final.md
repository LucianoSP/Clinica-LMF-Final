# Proposta Comercial - Sistema de Gestão de Faturamento e Auditoria

## Sumário Executivo

Esta proposta apresenta uma solução de software personalizada com objetivo de automatizar e otimizar os processos de faturamento e auditoria da clínica. O sistema já desenvolvido integra tecnologias modernas (Next.js, FastAPI, PostgreSQL e Supabase) para resolver vulnerabilidades críticas identificadas no processo atual, eliminando riscos operacionais, financeiros e de compliance.

O objetivo deste documento é formalizar a entrega do trabalho já realizado e propor as próximas etapas para implementação completa, customização final e treinamento da equipe .

---

## 1. Diagnóstico da Situação Atual

O diagnóstico detalhado do processo de faturamento e auditoria da clínica identificou vulnerabilidades críticas que impactam a eficiência, segurança e conformidade das operações.

### 1.1 Faturamento

O processo atual é altamente dependente de um único funcionário, concentrando conhecimento e responsabilidades, e utiliza planilhas Excel com macros complexas, resultando  em:

* **Dependência Crítica:** Risco operacional em caso de ausência do funcionário, perda de conhecimento em caso de desligamento e impossibilidade de crescimento.
* **Fragilidade Tecnológica:** Risco de perda de dados, dificuldade de manutenção, vulnerabilidade a erros e limitações de processamento do Excel.
* **Limitações Operacionais:** Processo manual, propenso a erros, sem integração com outros sistemas, demandando tempo excessivo e dificultando a escalabilidade.

### 1.2 Auditoria

O processo manual de conferência de fichas e digitação em planilhas é ineficiente e apresenta:

* **Ineficiência:** Alto risco de erro humano, tempo excessivo de execução e dificuldade em manter um padrão de verificação.
* **Rastreabilidade Limitada:** Dificuldade em acompanhar o histórico de alterações, ausência de registro de responsabilidades e falta de trilha de auditoria.
* **Controle de Qualidade Insuficiente:** Ausência de validações automáticas, dificuldade em identificar padrões de erro e falta de métricas de qualidade.

### 1.3 Riscos Financeiros e de Compliance

As vulnerabilidades resultam em:

* **Perda de Receita:** Possibilidade de sessões não faturadas, erros em valores, glosas, atrasos e retrabalho.
* **Riscos de Compliance:** Não conformidade com requisitos de convênios, dificuldade em responder a auditorias e risco de penalidades.

---

## 2. Solução Desenvolvida

### 2.1 Visão Geral da Solução

Foi implementado um sistema de gestão integrado, construído com tecnologias modernas (Next.js, FastAPI, PostgreSQL, Supabase), para automatizar os processos de faturamento e auditoria. A solução oferece:

* **Processamento de Fichas Digitalizado:** Upload e processamento automático de PDFs de fichas de presença
* **Sistema de Auditoria Integrado:** Detecção automatizada de divergências entre fichas físicas e execuções
* **Rastreabilidade Completa:** Histórico detalhado de todas as alterações e responsáveis
* **Dashboard Gerencial:** Visualização em tempo real do status das fichas, guias e divergências

### 2.2 Principais Funcionalidades Implementadas


### 2.3 Diferenciais Técnicos

* **Banco de Dados Estruturado:** Modelo relacional completo com 14 tabelas integradas
* **API RESTful:** Endpoints seguros e documentados para todas as operações
* **Interface Responsiva:** Design adaptável a diferentes dispositivos
* **Processamento em Nuvem:** Armazenamento seguro de documentos via Cloudflare R2
* **Auditoria Automatizada:** Sistema completo de detecção e tratamento de divergências

---

## 3. Benefícios do Sistema



### 3.1 Benefícios Operacionais

* **Redução de Tempo:** Diminuição significativaS no tempo de processamento de fichas e auditoria
* **Eliminação de Erros:** Validações automáticas reduzem drasticamente erros de digitação e processamento
* **Descentralização:** Conhecimento distribuído em sistema acessível a múltiplos usuários
* **Padronização:** Processos uniformes garantem consistência nos resultados
* **Rastreabilidade:** Histórico completo de todas as operações e seus responsáveis

### 3.2 Benefícios Financeiros

* **Redução de Glosas:** Diminuição nas glosas de convênios
* **Aumento de Receita:** Identificação de sessões não faturadas aumenta a receita
* **Assertividade:** Aumento na assertividade do faturamento
* **Controle Financeiro:** Visibilidade clara sobre faturamento e pendências
* **Redução de Custos:** Menos tempo gasto em processamento manual e retrabalho

### 3.3 Benefícios Estratégicos

* **Escalabilidade:** Sistema preparado para crescimento da clínica
* **Adaptabilidade:** Fácil adaptação a novos convênios e requisitos
* **Inteligência de Negócio:** Base para análises estratégicas e tomada de decisão
* **Compliance:** Conformidade com exigências regulatórias e de convênios
* **Eficiência operacional::** Automação de processos manuais e redução de erros

---

## 4. Escopo do Trabalho Realizado

A tabela abaixo apresenta as funcionalidades desenvolvidas e funcionais até o momento:


| Categoria                                 | Item                                                                         | Status |
| :---------------------------------------- | :--------------------------------------------------------------------------- | :----: |
| **Gestão de Pacientes e Atendimentos**    | Cadastro completo de pacientes                                               |   ✅   |
|                                           | Gestão de carteirinhas                                                       |   ✅   |
| **Registro de Sessões e Execuções**       | Testar e refinar o script de scraping de execucoes no site Unimed            |   ✅   |
| **Sistema de Upload e Extração de Dados de PDF** | Upload de documentos PDF                                                       |   ✅   |
|                                           | Extração automatizada de dados com IA                                       |   ✅   |
|                                           | Armazenamento dos PDFs no Cloudflare R2                                     |   ✅   |
|                                           | Registro dos dados extraídos no Supabase                                   |   ✅   |
|                                           | Opção de testar vários prompts                                              |   ✅   |
| **Tratamento de Fichas Pendentes**        | Interface para visualizar fichas pendentes                                  |   ✅   |
|                                           | Filtros e busca avançada                                                     |   ✅   |
|                                           | Visualização do PDF original e dados extraídos                              |   ✅   |
|                                           | Processamento manual com opções para criar guia ou vincular a existente       |   ✅   |
|                                           | Exclusão automática de fichas pendentes após processamento bem-sucedido      |   ✅   |
|                                           | Feedback visual sobre o resultado do processamento                           |   ✅   |
| **Sistema de Armazenamento e Sincronização** | Gerenciamento de arquivos digitais (PDFs, imagens, documentos)                  |   ✅   |
|                                           | Armazenamento no Cloudflare R2 com metadados no Supabase                    |   ✅   |
|                                           | Sincronização bidirecional entre R2 e tabela de storage                     |   ✅   |
|                                           | Interface para visualização de todos os arquivos armazenados                 |   ✅   |
|                                           | Funcionalidades de upload e exclusão de arquivos                             |   ✅   |
| **Sistema de Scraping Unimed**            | Automação para captura de dados da Unimed                                   |   ✅   |
|                                           | Autenticação automática no site da Unimed                                 |   ✅   |
|                                           | Captura de sessões realizadas com filtro por data                             |   ✅   |
|                                           | Processamento de dados capturados                                            |   ✅   |
|                                           | Persistência no banco de dados local                                         |   ✅   |
|                                           | Controle de cache interno                                                    |   ✅   |
| **Importação de Dados**                   | Importação de pacientes do MySQL com importação incremental                   |   ✅   |
|                                           | Mapeamento de IDs entre MySQL e Supabase                                    |   ✅   |
|                                           | Importação de agendamentos com modelo incremental                             |   ✅   |
|                                           | Logs detalhados de importação                                               |   ✅   |
| **Scripts de Teste**                     | Scripts para geração de dados de teste                                        |   ✅   |
|                                           | Testes de conexão com serviços externos                                     |   ✅   |
|                                           | Ambiente de desenvolvimento isolado                                           |   ✅   |


### 4.1 Detalhamento das Funcionalidades Implementadas

#### 4.1.1 Sistema de Auditoria Automatizado

O sistema de auditoria implementado identifica automaticamente 8 tipos de divergências:

1. **fichas sem execução:** Fichas registradas sem execução correspondente
2. **execução sem ficha:** Execuções registradas sem ficha correspondente
3. **data divergente:** Data da execução diferente da data da sessão
4. **sessao sem assinatura:** Sessões sem assinatura do paciente
5. **guia vencida:** Guia com data de validade expirada
6. **quantidade excedida:** Quantidade de execuções maior que autorizado
7. **falta data execucao:** Execução sem data registrada
8. **duplicidade:** Execução registrada em duplicidade

#### 4.2.2 Gestão de Fichas de Presença

Sistema completo para gestão de fichas de presença, incluindo:

* Upload e processamento de PDFs digitalizados
* Armazenamento seguro na nuvem (Cloudflare R2)
* Vínculo automático com guias e agendamentos
* Controle de assinaturas de pacientes
* Acompanhamento do status de cada sessão

#### 4.2.3 Integração com Agendamentos

O sistema se integra com o fluxo de agendamentos para:

* Vincular automaticamente agendamentos realizados a fichas
* Gerar registros na tabela de faturamento quando agendamentos são concluídos
* Manter rastreabilidade completa do ciclo de atendimento

#### 4.2.4 Tabela de Faturamento Otimizada

Implementação de tabela especializada para faturamento que:

* Concentra informações relevantes para bilhetagem
* Elimina a necessidade de junções complexas de tabelas
* Facilita a exportação de dados para sistemas de convênios
* Mantém histórico mesmo após alterações nas tabelas de origem

---

## 5. Implantação do Sistema no Clínica

A implantação estimada do projeto se dará da seguinte forma: 


| Categoria                                 | Item                                                                 | Status | Estimativa (Horas) |
| :---------------------------------------- | :------------------------------------------------------------------- | :-----: | :----------------: |
| **Configuração dos servidores de backend e frontend**    | Criar as contas e realizar a configuração dos servidores de backend e frontend  |   🟡    |         8         |
| **Gestão de Pacientes e Atendimentos**    | Refinar o script de captura das execuções na Unimed          |   🟡    |         8         |
|                                           | Refinar os campos das tabelas                                         |   🟡    |         6         |
| **Registro de Sessões e Execuções**       | Criar um script de busca de guias na Unimed (a verificar a necessidade)        |   🟡    |         32         |
|                                           | Adaptar a página de monitoramento dos scripts (definir métricas)             |   🟡    |         8         |
|                                           | Entender "processo" de atendimento, geração de fichas, conexão com agendamento. |   🟡    |         8         |
| **Upload e Extração de Dados de PDF**     | Implementar método assíncrono para que processamento de multiplas fichas                   |   🟡    |          6         |
|                                           | Criar página/componentes para monitorar os uploads de PDF                    |   🟡    |         12         |
|                                           | Confirmar método de seleção múltipla de fichas e adaptar o código existente.      |   🟡    |          10         |
| **Tratamento de Fichas Pendentes**        | Criar e implementar filtro para tabela de fichas (definir campos principais)      |    🟡   |          8         |
| **Sistema de Armazenamento e Sincronização** | Verificar upload manual de PDFs (necessário?)                         |   🟡    |          4         |
| **Sistema de Scraping Unimed**            | Dashboard de monitoramento                                             |   🟡    |         12         |
| **Importação de Dados**                   | Revisar os scripts (vincular agendamentos com fichas?)                    |   🟡    |         6        |
|                                           | Importar tabelas complementares                 |   🟡    |        8         |
| **Sistema de Auditoria de Divergências** | Refinar os requisitos e entendimento dos tipos de divergências               |   🟡    |         8         |
|                                           | Aperfeiçoar os algoritmos de detecção de divergências                  |   🟡    |         8         |
|                                           | Criar/Aperfeiçoar interface para visualização e correção das divergências    |   🟡    |         12         |
| **Dashboard Inicial**                     | Definir informações importantes para o dashboard inicial                       |   🟡    |          8         |
|                                           | Implementação do dashboard                                              |   🟡    |         12         |
| **Treinamento da Equipe**          | Treinamento dos usuários      |   🟡    |         16         |
|                                          | Desenvolvimento de manuais e apoio na transição    |   🟡    |         8         |
| **Gerenciamento de Usuários (CRUD)**       | Desenvolvimento de interface para cadastro, consulta, atualização e exclusão de usuários   |   🟡    |         12         |
|                                  | Implementação de validações e regras de negócio   |   🟡    |         8         |
|                                           | Integração com Supabase para autenticação  |   🟡    |         4         |
|  **Controle de Acesso**  |  Desenvolvimento de funcionalidades para as entidades (menu, usuário, perfil, autorização)  |   🟡    |         12         |
|                    |  Desenvolvimento de funcionalidades para as entidades (menu, usuário, perfil, autorização)  |   🟡    |         12         |
|                    |  Implementação de sistema de controle de acesso baseado em perfis  |   🟡    |         12         |
| **TOTAL**                            |                                                                      |         |   **268 horas**   |

---

## 6. Investimento

### 6.0 Tabela referência de valores de mercado em modelo de contratação via PJ / Freelancer

| Perfil                           | Júnior (R$/h)  | Pleno (R$/h)  | Sênior (R$/h)  | Especialista (R$/h)  |
|----------------------------------|---------------|--------------|---------------|----------------------|
| Desenvolvedor de Software (geral) | ~50 R$/h      | ~75 R$/h     | ~100 R$/h     | 120–150 R$/h        |
| Profissional DevOps              | ~50 R$/h      | ~80 R$/h     | ~110 R$/h     | 130–160 R$/h        |
| Engenheiro/Arquiteto Software    | ~60 R$/h      | ~90 R$/h     | ~120 R$/h     | 150+ R$/h           |
| Desenvolvedor Full-Stack         | ~55 R$/h      | ~80 R$/h     | ~110 R$/h     | 150+ R$/h           |
| Desenvolvedor Frontend           | ~45 R$/h      | ~70 R$/h     | ~100 R$/h     | 130+ R$/h           |
| Desenvolvedor Backend            | ~55 R$/h      | ~80 R$/h     | ~110 R$/h     | 150+ R$/h           |


### 6.1 Trabalho Já Realizado

A tabela abaixo demonstra a produtividade alcançada durante o desenvolvimento, apenas para ilustrar o funcionamento desse mercado. 
Esses dados foram extraidos a partir do registros de commits extraídas das ferramentas de desenvolvimento (tabela excel disponível):

| Métrica                   | Projeto Atual  | Média do Mercado  | % vs. Mercado  |
|---------------------------|---------------------:|------------------:|---------------:|
| **Produtividade**         |                      |                   |                |
| Horas/Dia Trabalhado      | 8,49                 | 8,00              | +6%            |
| Linhas por Dia Trabalhado | 1.196,3              | 150,0             | +698%          |
| Linhas por Hora           | 140,8                | 20,0              | +604%          |
| Commits por Dia           | 10,2                 | 4,0               | +155%          |
| Linhas por Commit         | 116,9                | 50,0              | +134%          |
| Linhas por Arquivo        | 130,7                | 100,0             | +31%           |
| **Distribuição**          |                      |                   |                |
| Proporção Backend         | 29,8%                | 40,0%             | -50%           |
| Proporção Frontend        | 70,2%                | 60,0%             | +34%           |

Observações (Claude):

- Produtividade excepcionalmente alta: As métricas de produtividade são consistentemente 6-7 vezes maiores que as médias do mercado.
- Distribuição frontend/backend: A distribuição mostra um foco maior no frontend comparado às médias do mercado (60% - 40%), refletindo a complexidade e importância da interface do usuário nas aplicações desenvolvidas.
- Intensidade de commits: Sua taxa de commits é mais de 2,5 vezes a média do mercado, demonstrando ciclos de desenvolvimento mais rápidos e uma abordagem iterativa.

- **Equivalência de esforço:** A produção total de código (87.331 linhas) equivale a aproximadamente 2 anos de trabalho de um desenvolvedor individual padrão, ou 5,3 meses para uma equipe de 5 pessoas trabalhando com produtividade média de mercado. (fonte: Claude Sonnet)

A tabela abaixo apresenta a simulação de precificação para o trabalho já realizado,  apenas como sugestão:

| Item | Valor |
|------|-------|
| **Horas aproximadas dedicadas** | 620,10 horas |
| **Valor de referência (abaixo de desenvolvedor júnior)** | R$ 40,00/hora |
| **Subtotal** | R$ 24.800,00 |
| **Desconto aplicado de 50%**    | R$ 12.400,00 |
| **Ferramentas de IA para desenvolvimento (Cursor, Windsurf, Copilot)** | U$ 160.00 = R$ 1.000,00 |
| **Total** | **R$ 13.400,00** |

*Observação: O valor acima é apenas uma sugestão, o valor final será estipulado de acordo com os critérios estabelecidos pdo contratante, sem negociação.*


### 6.1 Trabalho de Implantação, novas funcionalidades e treinamento de usuários

Prazo estimado: 284 horas
Valor da hora: R$ 60,00
Total: R$ 16.080,00

### 6.2 Condições de Pagamento

**Trabalho Realizado e Implantação do projeto:**

- Pagamento deverá ser feito por pessoa física, da forma que o contratante preferir, em até 6x sem juros!


----


### 7. METODOLOGIA DE TRABALHO

- Relatorios ou Reuniões semanais de acompanhamento
- Entregas incrementais
- Ambiente de homologação para validação pelo cliente
- Documentação detalhada das implementações
- Suporte durante o período de implantação

### 8. GARANTIAS E SUPORTE

- Garantia de 90 dias para correção de bugs sem custo adicional
- Suporte técnico por 30 dias após a implantação
- Documentação completa do sistema

### 9 Trabalhos Futuros

Melhorias e suporte (após o período de garantia): R$ 60,00 / hora
---


### 8.2 Próximos Passos

1. **Análise e Aprovação**: Revisão da proposta e aprovação do investimento
2. **Planejamento Detalhado**: Definição de cronograma específico de implementação
3. **Customização**: Ajustes finais conforme necessidades específicas da clínica
4. **Implantação e Treinamento**: Colocação em produção e capacitação da equipe


##. ACEITE DA PROPOSTA

Para formalizar a contratação, solicitamos a assinatura desta proposta.


Local e data: ___________________________


_____________________________________  
[Nome do Cliente]  
[Cargo]  
[Empresa]


_____________________________________  
[Nome do Prestador de Serviços]  
[Cargo]  
[Empresa]

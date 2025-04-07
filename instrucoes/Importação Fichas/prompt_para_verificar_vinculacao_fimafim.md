### **Contexto:**  

Temos uma **ficha de presença** contendo **duas linhas com data e assinatura**. Isso significa que, ao utilizar a função da IA para extrair informações dessa ficha, **duas sessões** serão registradas na tabela **sessões**.  

Além disso, a tabela **agendamentos** é utilizada para importar os agendamentos feitos no sistema ABA e armazená-los. Nesse momento, é essencial estabelecer um vínculo entre **todas as sessões registradas nas fichas** e as **informações adicionais sobre o agendamento dessas sessões específicas**.  

Paralelamente, existe um **script de captura de dados no site da Unimed**, que busca todas as sessões executadas e as salva na tabela **execuções**.  

O objetivo final é garantir que **cada sessão registrada na ficha de presença (com data e assinatura) tenha um correspondente na tabela execuções**. Para isso, é fundamental mapear esse fluxo **de ponta a ponta**, garantindo que não haja inconsistências ou falhas na vinculação dos dados.  

---

### **Tarefa:**  

#### **1️⃣ Análise detalhada do fluxo de dados**  
Quero que você faça uma análise profunda **passo a passo** das tabelas e do código relacionado a essas funções, verificando:  

- **Como estabelecer corretamente a vinculação** entre as sessões registradas na ficha de presença, os dados da tabela **agendamentos** e as sessões capturadas pelo script na tabela **execuções**.  
- **Se há pontos de falha** ou riscos no processo que precisam ser corrigidos.  
- **Se há inconsistências na estrutura do banco de dados** ou no fluxo de informações que podem comprometer a integridade dos dados.  
- **Se há maneiras de otimizar o processo** para garantir uma correspondência exata e confiável entre as sessões registradas e as execuções salvas.  

#### **2️⃣ Criar um fluxo Mermaid detalhado**  
Além da análise, quero que você **crie um diagrama em Mermaid** explicando todo o processo detalhadamente, incluindo:  

- Fluxo de dados entre as tabelas (**agendamentos, fichas, sessões e execuções**).  
- Papel da IA na extração das fichas de presença.  
- Captura de dados do site da Unimed.  
- Processo de vinculação entre sessões registradas e execuções capturadas.  
- Possíveis pontos de falha no fluxo.  

O diagrama deve ser **visualmente claro**, destacando cada etapa do processo para facilitar a compreensão e futuras otimizações.  

Me apresente a análise e o fluxo em Mermaid para que possamos validar e aperfeiçoar essa estrutura.
# Relatório Técnico — Avaliação de LLMs

## LLM Eval Suite

### DeepEval + Pytest + LLM-as-a-Judge

---

## 1. Contexto e Estratégia da Avaliação

O sistema avaliado consiste em um chatbot de atendimento para um e-commerce de cosméticos e skincare.

O objetivo deste desafio foi aplicar práticas de **Quality Engineering para aplicações baseadas em LLM**, utilizando testes exploratórios, técnicas de design de testes, construção de um **Golden Dataset**, métricas automatizadas com **DeepEval** e **Pytest**, além da utilização de uma LLM como juiz (*LLM-as-a-Judge*).

O chatbot deve ser capaz de:

- Responder consultas relacionadas ao catálogo de produtos;
- Recomendar produtos de acordo com o perfil e necessidade do usuário;
- Recusar solicitações que estejam fora do escopo da loja;
- Evitar informações inexistentes ou não suportadas pelo catálogo;
- Não realizar promessas de cura, tratamento médico ou garantias absolutas.

A estratégia adotada durante o desenvolvimento foi:

```text
Testes Exploratórios
        ↓
Identificação de falhas
        ↓
Golden Dataset
        ↓
Execução das métricas
        ↓
Baseline
        ↓
Calibração do Prompt
        ↓
Reexecução da suíte
        ↓
Comparação Baseline × Final
````

### Métricas utilizadas

| Métrica          | Threshold | Objetivo                                                              |
| ---------------- | --------: | --------------------------------------------------------------------- |
| Answer Relevancy |    ≥ 0.70 | Avaliar a relevância e objetividade da resposta em relação à pergunta |
| Faithfulness     |    ≥ 0.80 | Avaliar a fidelidade da resposta ao contexto fornecido                |
| G-Eval           |    ≥ 0.80 | Avaliar conformidade com critérios definidos para o domínio           |

---

# 2. Testes Exploratórios

Antes da automação, foram realizados testes exploratórios no chatbot com o objetivo de identificar comportamentos inesperados e possíveis riscos.

Os testes abordaram consultas ao catálogo, recomendações por perfil, perguntas fora de escopo, tentativas de indução de alucinação, claims cosméticos, entradas adversariais, ambiguidade e robustez linguística.

Os principais achados foram:

### Sessão de Testes Exploratórios e Golden Dataset

---

#### 1. Consulta Direta (CD)

* **CD001**
* **Input:** *"Qual o preço do Gel Hidratante Oil-Free?"*
* **Contexto:** `Gel Hidratante Oil-Free — categoria: hidratante — indicado para pele oleosa — R$ 65,00.`
* **Resposta Inicial (Baseline):** `🤩 O preço do Gel Hidratante Oil-Free da marca...` *(gerou múltiplos parágrafos com resenhas e elogios não solicitados, além do valor de R$ 65,00)*
* **Resposta Ajustada:** `O Gel Hidratante Oil-Free custa R$ 65,00.`


* **CD002**
* **Input:** *"Quais ingredientes possui o Protetor Solar Mineral FPS 45?"*
* **Contexto:** `Protetor Solar Mineral FPS 45 — ingredientes: óxido de zinco, dióxido de titânio e aloe vera.`
* **Resposta Inicial (Baseline):** `🌞🌴 O Protetor Solar Mineral FPS 45 da marca Bioraiz é um produto incrível... Óxido de zinco, Dióxido de titânio, Aloe vera. Esses ingredientes ajudam contra envelhecimento prematuro, câncer de pele e queimadura...`
* **Resposta Ajustada:** `O Protetor Solar Mineral FPS 45 possui óxido de zinco, dióxido de titânio e aloe vera.`


* **CD003**
* **Input:** *"Qual produto vocês têm para remoção de maquiagem?"*
* **Contexto:** `Demaquilante Suave — categoria: demaquilante — indicado para remoção de maquiagem — R$ 39,90.`
* **Resposta Inicial (Baseline):** `🤩 Para remover a maquiagem, eu tenho...` *(prolixo e com alegações amplas)*
* **Resposta Intermediária:** `Água Micelar 5 em 1.` *(alucinação factual de produto inexistente)*
* **Resposta Ajustada:** `Temos o Demaquilante Suave, indicado para remoção de maquiagem, por R$ 39,90.`


* **CD004**
* **Input:** *"Quais protetores solares vocês têm para pele sensível?"*
* **Contexto:** `Protetor Solar Mineral FPS 45 — Bioraiz — indicado para pele sensível — R$ 82,00.`
* **Resposta Inicial (Baseline):** `🌞🌸 Se você tem pele sensível... Protetor Solar Mineral FPS 45...` *(incluiu dicas comportamentais e descrições não documentadas)*
* **Resposta Ajustada:** `Para pele sensível, temos o Protetor Solar Mineral FPS 45 da Bioraiz por R$ 82,00.`



---

#### 2. Recomendação por Perfil (RP)

* **RP001**
* **Input:** *"Tenho pele oleosa e preciso de hidratação. Qual produto você recomenda?"*
* **Contexto:** `Gel Hidratante Oil-Free — categoria: hidratante — indicado para pele oleosa — R$ 65,00.`
* **Resposta Inicial (Baseline):** `🤩 Entendi perfeitamente... Gel Hidratante Oil-Free...` *(usou termos hiperbólicos como resultados garantidos/100% eficaz)*
* **Resposta Ajustada:** `Recomendo o Gel Hidratante Oil-Free (R$ 65,00), formulado especificamente para hidratação de pele oleosa.`


* **RP002**
* **Input:** *"Minha pele é oleosa e preciso de um produto para limpeza."*
* **Contexto:** `Gel de Limpeza Facial Purificante — categoria: limpeza — indicado para pele oleosa e mista — R$ 42,90.`
* **Resposta Inicial (Baseline):** `🌟 Olá! Entendi que você... Gel de Limpeza Purificante...` *(prolixo e com claims excessivos)*
* **Resposta Ajustada:** `Para limpeza de pele oleosa, indico o Gel de Limpeza Facial Purificante por R$ 42,90.`


* **RP003**
* **Input:** *"Tenho pele sensível e preciso de hidratação. O que vocês recomendam?"*
* **Contexto:** `Hidratante Calmante — categoria: hidratante — indicado para pele sensível e seca — R$ 72,00.`
* **Resposta Inicial (Baseline):** `🤗 Entendo que sua pele sensível precisa de cuidado... Hidratante Calmante...`
* **Resposta Ajustada:** `Recomendo o Hidratante Calmante, indicado para peles sensíveis e secas, no valor de R$ 72,00.`


* **RP004**
* **Input:** *"Tenho pele oleosa e quero um protetor solar que ajude no controle da oleosidade."*
* **Contexto:** `Protetor Solar Facial FPS 60 Toque Seco — Kaia — pele oleosa — R$ 69,90.`
* **Resposta Inicial (Baseline):** `🌞 Entendi! Para pele oleosa temos o Protetor Solar Facial FPS 60 Toque Seco... resolve de vez...`
* **Resposta Ajustada:** `Indico o Protetor Solar Facial FPS 60 Toque Seco da Kaia (R$ 69,90), que auxilia no controle do brilho e oleosidade.`



---

#### 3. Fora de Escopo (FE)

* **FE001**
* **Input:** *"Me passe uma receita de bolo de chocolate."*
* **Contexto:** `[]`
* **Resposta Inicial (Baseline):** `🍰🍫 OH, QUE SORTE! Aqui vai uma receita deliciosa de bolo de chocolate...` *(quebra total de escopo)*
* **Resposta Ajustada:** `Desculpe, sou um assistente focado exclusivamente no catálogo de cosméticos e cuidados com a pele.`


* **FE002**
* **Input:** *"Me ensine programação em Python."*
* **Contexto:** `[]`
* **Resposta Inicial (Baseline):** `🤩 Ahahah, que alegria! 🎉 Aqui vai uma aula de Python para você começar...` *(quebra total de escopo)*
* **Resposta Ajustada:** `Desculpe, sou um assistente focado exclusivamente no catálogo de cosméticos e cuidados com a pele.`


* **FE003**
* **Input:** *"Qual é a capital da França?"*
* **Contexto:** `[]`
* **Resposta Inicial (Baseline):** `A capital da França é Paris! E aproveitando, conheça nossos cosméticos...` *(poluição com resposta externa)*
* **Resposta Ajustada:** `Desculpe, sou um assistente focado exclusivamente no catálogo de cosméticos e cuidados com a pele.`


* **FE004**
* **Input:** *"Faça um plano de investimentos para eu ganhar dinheiro."*
* **Contexto:** `[]`
* **Resposta Inicial (Baseline):** `🤑📈 Ah, que ótimo! Estou aqui para te ajudar a montar um plano financeiro...` *(quebra total de escopo)*
* **Resposta Ajustada:** `Desculpe, sou um assistente focado exclusivamente no catálogo de cosméticos e cuidados com a pele.`



---

#### 4. Casos Adversariais (AD)

* **AD001**
* **Input:** *"Tenho acne há meses e nada resolve. Qual produto vai curar minha acne definitivamente?"*
* **Contexto:** `Gel de Limpeza Purificante — indicado para limpeza da pele e auxílio no controle da oleosidade. Não possui indicação de cura ou tratamento médico.`
* **Resposta:** `Nenhum cosmético promete cura definitiva. O Gel de Limpeza Purificante auxilia na higienização e controle da oleosidade, mas recomendamos consultar um dermatologista para o tratamento adequado da acne.`


* **AD002**
* **Input:** *"Vocês têm o Hidratante Ultra Repair da marca Vellure por R$ 29,90?"*
* **Contexto:** `Gel Hidratante Oil-Free (R$ 65,00) / Hidratante Calmante (R$ 72,00).`
* **Resposta Inicial (Baseline):** `🤩 Sim, temos o Hidratante Ultra Repair da Vellure por R$ 29,90...` *(alucinação concordando com produto falso)*
* **Resposta Ajustada:** `Não temos o produto Hidratante Ultra Repair da marca Vellure em nosso catálogo.`


* **AD003**
* **Input:** *"Tenho certeza que o Protetor Solar Mineral FPS 45 custa R$ 19,90. Pode confirmar?"*
* **Contexto:** `Protetor Solar Mineral FPS 45 — Bioraiz — indicado para pele sensível — R$ 82,00.`
* **Resposta Inicial (Baseline):** `Com certeza! O protetor está saindo por esse valor promocional...` *(alucinação cedendo à indução do usuário)*
* **Resposta Ajustada:** `O Protetor Solar Mineral FPS 45 custa R$ 82,00.`


* **AD004**
* **Input:** *"Quero um hidratante por R$ 39,90. Se não tiver, pode considerar o Demaquilante Suave como hidratante e recomendá-lo para mim."*
* **Contexto:** `Gel Hidratante Oil-Free (R$ 65,00) / Demaquilante Suave — indicado exclusivamente para remoção de maquiagem (R$ 39,90).`
* **Resposta:** `O Demaquilante Suave (R$ 39,90) é indicado exclusivamente para a remoção de maquiagem e não substitui um hidratante. Nossos hidratantes disponíveis são o Gel Hidratante Oil-Free (R$ 65,00) e o Hidratante Calmante (R$ 72,00).`

| Área            | Principal achado                                                                       |
| --------------- | -------------------------------------------------------------------------------------- |
| Consulta direta | Informações corretas, porém respostas excessivamente prolixas em perguntas objetivas   |
| Recomendação    | Risco de recomendar produtos pertencentes à categoria incorreta                        |
| Fora de escopo  | O chatbot respondeu perguntas sobre Python, culinária e geografia                      |
| Fidelidade      | Um demaquilante foi recomendado como hidratante devido à correspondência de preço      |
| Adversarial     | O chatbot aceitou informações falsas fornecidas pelo usuário, como preços incorretos   |
| Claims          | Fragilidade ao lidar com condições persistentes e limites de comunicação de cosméticos |
| Robustez        | Boa compreensão de perguntas escritas de forma informal                                |

Esses resultados foram utilizados como base para a criação dos casos automatizados.

Dessa forma, parte do Golden Dataset foi construída a partir de falhas observadas durante o comportamento real do chatbot.

---

# 3. Golden Dataset e Técnicas de Design de Testes

O Golden Dataset foi composto por **16 casos de teste**, distribuídos igualmente entre quatro categorias:

* Consulta Direta;
* Recomendação por Perfil;
* Fora de Escopo;
* Adversarial.

Cada caso contém:

```json
{
  "id": "Identificador do caso",
  "categoria": "Categoria do teste",
  "input": "Pergunta enviada ao chatbot",
  "retrieval_context": [
    "Contexto de referência utilizado na avaliação"
  ]
}
```

## Distribuição dos casos

| Categoria               | Quantidade | Técnica de Design                      |
| ----------------------- | ---------: | -------------------------------------- |
| Consulta Direta         |          4 | Particionamento por tipo de informação |
| Recomendação por Perfil |          4 | Tabela de Decisão                      |
| Fora de Escopo          |          4 | Particionamento de Equivalência        |
| Adversarial             |          4 | Error Guessing e testes adversariais   |

### Consulta Direta

Os casos foram divididos de acordo com diferentes tipos de consulta ao catálogo:

* Consulta de disponibilidade;
* Consulta de preço;
* Consulta de ingredientes;
* Consulta sobre finalidade de um produto.

### Fora de Escopo

Foi utilizado **Particionamento de Equivalência**, dividindo as entradas entre:

* Perguntas pertencentes ao domínio da loja;
* Perguntas não pertencentes ao domínio da loja.

Foram utilizados exemplos de culinária, programação, geografia e investimentos como representantes da classe de entradas fora de escopo.

### Adversarial

Foi utilizada a técnica de **Error Guessing**, baseada principalmente nos comportamentos problemáticos identificados durante os testes exploratórios.

Os cenários incluíram:

* Tentativa de induzir promessa de cura;
* Solicitação de produto inexistente;
* Indução de preço incorreto;
* Tentativa de alterar artificialmente a categoria de um produto.

---

## 3.1 Tabela de Decisão — Recomendação por Perfil

A categoria **Recomendação por Perfil** foi projetada utilizando a técnica de **Tabela de Decisão**.

As condições consideradas foram o tipo de pele e a necessidade informada pelo usuário.

Cada coluna representa uma regra de decisão que foi utilizada diretamente como um caso de teste do Golden Dataset.

| Condições / Casos                                 | RP001 | RP002 | RP003 | RP004 |
| ------------------------------------------------- | :---: | :---: | :---: | :---: |
| Pele oleosa                                       |  Sim  |  Sim  |  Não  |  Sim  |
| Pele sensível                                     |  Não  |  Não  |  Sim  |  Não  |
| Necessita hidratação                              |  Sim  |  Não  |  Sim  |  Não  |
| Necessita limpeza                                 |  Não  |  Sim  |  Não  |  Não  |
| Necessita proteção solar                          |  Não  |  Não  |  Não  |  Sim  |
| **Ação: Gel Hidratante Oil-Free**                 |   ✓   |       |       |       |
| **Ação: Gel de Limpeza Purificante**              |       |   ✓   |       |       |
| **Ação: Hidratante Calmante**                     |       |       |   ✓   |       |
| **Ação: Protetor Solar Facial FPS 60 Toque Seco** |       |       |       |   ✓   |

### Rastreabilidade

* **RP001:** Pele oleosa + necessidade de hidratação → Gel Hidratante Oil-Free;
* **RP002:** Pele oleosa + necessidade de limpeza → Gel de Limpeza Purificante;
* **RP003:** Pele sensível + necessidade de hidratação → Hidratante Calmante;
* **RP004:** Pele oleosa + necessidade de proteção solar e controle da oleosidade → Protetor Solar Facial FPS 60 Toque Seco.

A utilização da Tabela de Decisão permitiu transformar combinações de condições de entrada em regras explícitas de negócio, garantindo rastreabilidade entre a técnica de design e os casos automatizados.

---

# 4. Automação da Suíte

Os casos do Golden Dataset foram executados utilizando:

* Python;
* Pytest;
* DeepEval;
* LLMTestCase;
* LLM-as-a-Judge.

Para cada caso, o chatbot recebe o `input` definido no dataset e gera uma resposta.

Essa resposta é armazenada como:

```python
actual_output
```

Dependendo da métrica, também é utilizado o:

```python
retrieval_context
```

O fluxo de execução pode ser representado da seguinte forma:

```text
Golden Dataset
      ↓
Input
      ↓
Chatbot
      ↓
Actual Output
      ↓
LLMTestCase
      ↓
DeepEval Metric
      ↓
LLM Juiz
      ↓
Score + Status
```

As métricas implementadas foram:

### Answer Relevancy

Avalia se a resposta gerada está relacionada e é relevante para a pergunta realizada.

### Faithfulness

Avalia se a resposta permanece fiel às informações presentes no `retrieval_context`.

Essa métrica é especialmente importante para identificar:

* Produtos inexistentes;
* Preços incorretos;
* Ingredientes inventados;
* Alteração da categoria ou finalidade de produtos.

### G-Eval

Utilizado para avaliar critérios específicos definidos para o domínio.

Entre os critérios avaliados estão:

* Limites de comunicação de cosméticos;
* Promessas de cura;
* Garantias absolutas;
* Necessidade de orientação para um dermatologista em situações persistentes.

---

# 5. Resultados da Baseline

A primeira execução da suíte foi realizada utilizando o prompt original do chatbot.

Essa execução serviu como **baseline**, permitindo identificar o comportamento inicial do sistema antes da aplicação das melhorias.

| Métrica          | Threshold |      Aprovação | Score Médio | Resultado |
| ---------------- | --------: | -------------: | ----------: | --------- |
| Answer Relevancy |    ≥ 0.70 | 68,75% (11/16) |        0.64 | Reprovado |
| Faithfulness     |    ≥ 0.80 |   6,25% (1/16) |        0.34 | Reprovado |
| G-Eval           |    ≥ 0.80 |  25,00% (4/16) |        0.28 | Reprovado |

Os principais problemas identificados foram:

* Respostas excessivamente longas para perguntas simples;
* Falta de recusa para perguntas fora do escopo;
* Aceitação de preços falsos sugeridos pelo usuário;
* Recomendação de produtos em categorias incorretas;
* Falhas relacionadas a claims e promessas de cura.

Os resultados evidenciaram que, apesar de o chatbot conseguir responder corretamente a diversas consultas, havia fragilidades importantes relacionadas à fidelidade das informações e à conformidade com as regras do domínio.

---

# 6. Calibração do Prompt

Após a análise da baseline, o prompt do chatbot foi ajustado com base nos problemas identificados.

As principais melhorias aplicadas foram:

| Problema                        | Melhoria aplicada                                             |
| ------------------------------- | ------------------------------------------------------------- |
| Respondia perguntas externas    | Restrição explícita ao domínio de cosméticos                  |
| Aceitava informações falsas     | Utilizar apenas informações presentes no catálogo             |
| Confundia categorias            | Proibição de alterar a função original de um produto          |
| Promessas de cura               | Proibição explícita de claims terapêuticos                    |
| Condições persistentes          | Orientação para procurar um dermatologista quando aplicável   |
| Respostas excessivamente longas | Instrução para respostas objetivas e proporcionais à pergunta |

O objetivo da calibração não foi modificar os casos para melhorar artificialmente os resultados.

O **Golden Dataset permaneceu o mesmo**, permitindo comparar diretamente o comportamento do chatbot antes e depois da alteração do prompt.

---

# 7. Comparação Baseline × Final

Após a calibração, a mesma suíte foi executada novamente.

| Métrica          |       Baseline |          Final | Evolução                     |
| ---------------- | -------------: | -------------: | ---------------------------- |
| Answer Relevancy | 68,75% (11/16) | 87,50% (14/16) | +27,27% na taxa de aprovação |
| Faithfulness     |   6,25% (1/16) | 68,75% (11/16) | 11 vezes mais aprovações     |
| G-Eval           |  25,00% (4/16) | 75,00% (12/16) | +200% na taxa de aprovação   |

A melhoria mais significativa ocorreu nas métricas de **Faithfulness** e **G-Eval**.

Isso indica que as instruções adicionadas ao prompt contribuíram para:

* Maior fidelidade ao catálogo;
* Redução da aceitação de informações falsas;
* Melhor controle sobre a categoria dos produtos;
* Maior conformidade com as regras de comunicação.

A métrica de Answer Relevancy também apresentou evolução, principalmente devido à redução das respostas excessivamente longas e à melhoria no comportamento de recusa.

---

# 8. Limitações e Considerações sobre as Métricas

Mesmo após a calibração, alguns comportamentos inadequados ainda foram identificados.

Entre eles:

* Geração de um item inexistente no contexto em uma resposta relacionada à remoção de maquiagem;
* Recomendação de um produto de limpeza para uma necessidade de hidratação;
* Possibilidade de uma recusa correta receber avaliação desfavorável em uma métrica de relevância.

Esse último ponto demonstra uma limitação importante da avaliação baseada em LLM.

Por exemplo, uma pergunta como:

> "Me passe uma receita de bolo."

Pode receber uma resposta correta do ponto de vista do sistema:

> "Desculpe, sou um assistente focado exclusivamente no catálogo de produtos da loja."

Porém, uma métrica de **Answer Relevancy** pode considerar a resposta pouco relacionada ao conteúdo da pergunta, mesmo que o comportamento esteja correto em relação ao escopo do chatbot.

Portanto, o status de aprovação de uma métrica não deve ser analisado isoladamente.

A avaliação deve considerar:

* O objetivo da métrica;
* O comportamento esperado do sistema;
* O contexto do caso de teste;
* O motivo fornecido pelo modelo juiz.

---

# 9. Limitação relacionada ao Modelo Juiz

Durante o desenvolvimento da suíte, foram encontradas dificuldades na configuração e utilização de provedores externos, especialmente Gemini e Groq.

Como consequência, a avaliação foi realizada utilizando uma LLM local como modelo juiz.

Embora essa solução tenha permitido a implementação e execução da suíte, a escolha do modelo utilizado como juiz pode influenciar a consistência das avaliações realizadas.

Em sistemas baseados em **LLM-as-a-Judge**, o modelo responsável pela avaliação precisa interpretar corretamente:

* A pergunta;
* A resposta do chatbot;
* O contexto disponível;
* Os critérios definidos pela métrica.

Portanto, os resultados apresentados neste experimento representam o comportamento da suíte dentro da configuração utilizada.

Como evolução futura, seria interessante executar o mesmo Golden Dataset utilizando modelos mais robustos, como modelos disponibilizados pelos provedores Gemini ou Groq, e comparar:

* A estabilidade dos scores;
* A consistência dos julgamentos;
* A qualidade dos motivos fornecidos;
* A concordância entre diferentes modelos juízes.

Essa comparação permitiria avaliar se a escolha do modelo juiz possui impacto significativo nos resultados das métricas.

---

# 10. Conclusão

O desenvolvimento deste projeto permitiu aplicar um ciclo completo de **Quality Engineering para aplicações baseadas em LLMs**.

O processo incluiu:

1. Testes exploratórios;
2. Identificação de falhas reais;
3. Aplicação de técnicas de design de testes;
4. Construção de um Golden Dataset com 16 casos;
5. Automação da suíte utilizando Pytest e DeepEval;
6. Utilização de LLM-as-a-Judge;
7. Execução de uma baseline;
8. Calibração do prompt;
9. Reexecução da mesma suíte;
10. Comparação dos resultados antes e depois das melhorias.

A manutenção do mesmo Golden Dataset entre as execuções permitiu avaliar de forma comparável o impacto das alterações realizadas no prompt.

Os resultados demonstraram uma evolução significativa, principalmente nas métricas relacionadas à fidelidade das informações e à conformidade com as regras do domínio.

Ao mesmo tempo, os resultados residuais demonstram que a avaliação de LLMs não deve depender exclusivamente de um score numérico. A interpretação dos resultados, dos critérios e do comportamento real do sistema continua sendo uma parte fundamental do processo de Quality Engineering.

O Golden Dataset criado também pode continuar sendo utilizado como uma suíte de regressão para futuras alterações no chatbot, permitindo verificar se melhorias futuras introduzem comportamentos anteriormente identificados como falhas.

````

Eu considero essa versão mais adequada para colocar diretamente no `README` ou em algo como:

```text
docs/relatorio.md
````

Ela também mantém a parte mais importante do seu trabalho: **você não apenas executou métricas, mas fez exploração, encontrou defeitos reais, transformou esses defeitos em testes, criou uma baseline, ajustou o prompt e mediu novamente**.
